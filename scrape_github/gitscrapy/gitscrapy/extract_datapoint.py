import requests
from pprint import pprint
import base64
from github import Github
import json
from progress.bar import Bar

import re
from bs4 import BeautifulSoup
import urllib.request


def find_top_repos(n, repos):
    '''Find top repos of a user'''
    top_repos = []
    top_stars = []

    # the repo with smallest number of stars in the array
    min_stars = float('-inf')
    min_index = -1

    if len(repos) <= n:
        return repos

    for i, repo in enumerate(repos):

        if len(top_repos) != n:
            if min_stars <= repo.stargazers_count:
                min_stars = repo.stargazers_count
                min_index = i
            top_repos.append(repo)
            top_stars.append(repo.stargazers_count)

        else:
            if min_stars < repo.stargazers_count:
                min_stars = min(top_stars)
                min_index = top_stars.index(min(top_stars))
                top_stars.pop(min_index)
                top_repos.pop(min_index)
                top_repos.append(repo)
                top_stars.append(repo.stargazers_count)
    return top_repos


def get_repo(user_name, repo, new_users, contributor, username, token):


    # repository full name
    # full_name = repo.full_name
    # repository description
    description = repo['description']
    # the date of when the repo was created
    # created_at = repo['created_at
    # the date of then the repo was updated_at
    updated_at = repo['updated_at']
    # programming language
    language = repo['language']
    # number of forks
    forks = repo['forks']
    # number of stars
    num_stars = repo['stargazers_count']
    # readme
    # readme = repo.get_readme().decoded_content
    #  contributors
    if not contributor:
        try:
            contributors_url = repo['contributors_url']
            contributors = requests.get(
                contributors_url, auth=(username, token)).json()
            contributors = [contributor['login'] for contributor in contributors if contributor['login'] != user_name]
            new_users += contributors
            new_users = list(set(new_users))
        except:
            pass

    return [description, updated_at, language, forks, num_stars]


def find_repo_info(user_name, repos, new_users, contributor, username, token):

    if len(repos) == 0:
        return None, None, None, None, None, None

    max_star = float('-inf')
    total_stars = 0
    forks = 0
    languages = []
    descriptions = []
    dates = []

    with Bar('Extract_repo', max=len(repos)) as bar:
        for repo in repos:
            repo_info = get_repo(user_name, repo, new_users, contributor, username, token)
            descriptions.append(repo_info[0])
            dates.append(repo_info[1])
            languages.append(repo_info[2])
            forks += repo_info[3]
            num_stars = repo_info[4]
            total_stars += num_stars
            if max_star < num_stars:
                max_star = num_stars

            bar.next()

    return total_stars, forks, languages, descriptions, dates, max_star


def extract_profile(user, new_users, username, token, contributor=False, n=5):


    # Contributor or Owner
    if contributor == False:
        type_user = 'Owner'
    else:
        type_user = 'Contributor'

    user_name = user['login']
    name = user['name']
    html_url = user['html_url']
    bio = user['bio']
    company = user['company']
    email = user['email']
    followers = user['followers']
    following = user['following']
    hireable = user['hireable']
    location = user['location']
    created_at = user['created_at']
    updated_at = user['updated_at']

    i = 1
    repos = []
    while True:
        repos_url = user['repos_url'] + '?page=' + str(i)
        print('repos_url', i, repos_url) 
        repos_i = requests.get(repos_url , auth=(username, token)).json()

        if len(repos_i) == 0:
            break
        
        else:
            print(len([repo for repo in repos_i if repo['fork'] == False]))
            repos += [repo for repo in repos_i if repo['fork'] == False]
            i += 1
    # top_repos = find_top_repos(n, repos)

    total_stars, forks, languages, descriptions, dates, max_star= find_repo_info(
        user_name, repos, new_users, contributor, username, token)

    return [user_name, name, type_user, html_url, bio, company, email, followers,
            following, hireable, location, created_at, updated_at, total_stars, max_star,
            forks, languages, descriptions, dates
            ]


def extract_contributions(url, token):

    headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.11 (KHTML, like Gecko) '
               'Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive',
               'Authorization': 'token %s' % token}

    req= urllib.request.Request(url=url, headers=headers)
    source= urllib.request.urlopen(req).read()

    soup= BeautifulSoup(source, 'lxml')

    contribution= soup.find_all('h2', class_='f4 text-normal mb-2')[0].text

    print(int(re.findall('\d+', contribution)[0]))

    return int(re.findall('\d+', contribution)[0])

def extract_request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
               'AppleWebKit/537.11 (KHTML, like Gecko) '
               'Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}


    url = urllib.request.Request(url=url, headers=headers)
    source = urllib.request.urlopen(url).read()
    encoding = source.decode("utf-8")
    dic = json.loads(encoding)
    return dic 
