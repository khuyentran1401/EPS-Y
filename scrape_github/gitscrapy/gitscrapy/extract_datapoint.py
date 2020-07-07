import requests
from pprint import pprint
import base64
from github import Github
import json
from progress.bar import Bar

import re
from bs4 import BeautifulSoup
import urllib.request
import datapane as dp

from collections import Counter
import pickle
import pandas as pd 
import  numpy as np

from process_data import process_df
import time


class GithubUserScrape:
    '''Class to scrape Github profiles

    Parameters
    ----------
    file_name: str  
        json file's name that contains the urls of top machine learning repos

    username: str
        Authenticated username 
    
    token: str
        Token of authenticated user

    num_repos: int
        Number of repositories to scrape

    repo: list
        Repos to scrape (default is None)

    scrape_owner: bool
        Whether to scrape the owners of the repos. 
        If False, use pickle.load (default is True)

    continue_scraping: bool
        Whether to continue the last scraping.
        If False, use pickle.load (default is False)


    Attributes
    ----------
    

    '''

    def __init__(self, file_name, username, token, num_repos=None, scrape_owner=True, continue_scraping=False):

        self.file_name = file_name
        self.username = username
        self.token = token
        self.num_repos = num_repos
        self.scrape_owner = scrape_owner
        self.continue_scraping = continue_scraping


    def scrape(self):
        '''Get information of both owner and contributors'''

        if self.scrape_owner == True:
            self.find_repo_list()
            self.owner_info()

        else:
            self.new_users = pickle.load(open("new_users", 'rb'))
            self.info = pickle.load(open('owner_info', 'rb'))
            self.top_repo_contributions = pickle.load(open('top_repo_contributions', 'rb'))
            

        if self.continue_scraping == True:
            self.info = pickle.load(open('intermediate_info', 'rb'))

            # User whether the scrape stopped
            stop_user = self.info[-1][0]
            print(stop_user)
            
            stop_user_index = self.new_users.index(stop_user)
            self.new_users = self.new_users[stop_user_index:]
            self.info = self.info[:-1]
        
        self.contributor_info()
            


        

        # Create dataframe to hold new information
        self.repo_df = pd.DataFrame(np.array(self.info), columns=['user_name', 'name', 'type_user', 'html_url', 'bio', 'company', 'email', 'followers',
                                                        'following', 'hireable', 'location', 'created_at', 'updated_at', 'total_stars', 
                                                        'max_star', 'forks', 'languages', 'descriptions', 'dates', 'readmes'])

        #self.contributions_info()

        #self.merge_df()

        pickle.dump(self.repo_df, open('test_df', 'wb'))

    def find_repo_list(self):
        ''' Find urls and repo's names to extract '''

        self.repos = []

        with open(self.file_name) as f:
            data = json.load(f)
            with Bar('Extract_repo_list', max=len(data)) as bar:
                for page in data:
                    self.repos += page['repo_name']
                    bar.next()

    def owner_info(self):
        '''Get information of the owner of the repos and find contributors
        info: nested list
            List of all users' information
        
        new_users: list
            List of contributors found from top repos

        top_repo_contributions: dict
            Contributions of users to the top repos. 
            Keys are the users and values are the sum of contributions of different top repos
        
        '''
    
        self.info = []
        self.new_users = []
        self.top_repo_contributions = {}

        if self.num_repos == None:
            self.num_repos = len(self.repos)

        with Bar('Extract_user_info', max=len(self.repos[:self.num_repos])) as bar:
            for i, repo in enumerate(self.repos[:self.num_repos]):
                user = repo.split('/')[0]
                print('\n',i, user)

                url = 'https://api.github.com/users/' + user
                user = requests.get(url, auth=(self.username, self.token)).json()

                # Exclude organization
                if user['type'] == 'User' and user['public_repos'] <= 1000:
                    user_info = self.extract_profile(user)     
                    self.info.append(user_info)
                else:
                    pass
                bar.next()

        pickle.dump(self.info, open("owner_info", 'wb'))

        # get unique users
        self.new_users = list(set(self.new_users))
        pickle.dump(self.new_users, open("new_users", 'wb'))

        pickle.dump(self.top_repo_contributions, open('top_repo_contributions', 'wb'))

    def contributor_info(self):
        '''Get information about the contributors'''


        with Bar('Extract_contributor_info', max=len(self.new_users)) as bar:
            for user in self.new_users: 
                
                
                url = 'https://api.github.com/users/' + user
                user = requests.get(url, auth=(self.username, self.token)).json()

                if user['type'] == 'User' and user['public_repos'] <= 1000:

                    contributor_info = self.extract_profile(user, contributor=True)
                    self.info.append(contributor_info)

                pickle.dump(self.info, open('intermediate_info', 'wb'))


                bar.next()
                
                
                
    def contributions_info(self):
        '''Extract the contributions of users'''
    
        urls = list(self.repo_df.html_url)

        self.contributions = []
        self.exceptions = []

        with Bar('Extract_contributions', max=len(urls)) as bar:

            for url in urls:
                time.sleep(5)
                try:
                    contribution = self.extract_contributions(url)
                    self.contributions.append(contribution)
                except:
                    self.exceptions.append(url)
                
                bar.next()


    def merge_df(self):
        '''Merge contributions last year, contributions in the top repos, and the existing dataframe'''

        # Find the indices of users to exclude
        exclude_ind = []

        for i, url in enumerate(self.repo_df.html_url):
            if url in self.exceptions:
                exclude_ind.append(i)

        # Remove the users without the contributions
        self.repo_df = self.repo_df[~self.repo_df.index.isin(exclude_ind)]

        self.repo_df.reset_index(inplace=True)
        self.repo_df = self.repo_df.drop('index', axis=1)

        self.repo_df['contribution'] = self.contributions

        # Process df
        self.repo_df = process_df(self.repo_df)

        user_names = list(self.repo_df.user_name)

        # Merge top_repos_contributions
        top_contributions = {
            key: value for key, value in self.top_repo_contributions.items() if key in user_names}

        self.repo_df['top_repo_contributions'] = [0] * len(self.repo_df)

        # Assign the top_contribution values to the user
        for key, value in top_contributions.items():
            self.repo_df.loc[self.repo_df.user_name ==
                             key, 'top_repo_contributions'] = value


    def extract_profile(self, user, contributor=False):
        '''Extract profile of users
        
        Parameters
        ----------
        user: dict
            Information of the users in their profile page

        contributor: bool, optional
            Whether a user is the contributor of the repo (default is False)

        '''

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

        # Find the urls of all Github repos of the user
        i = 1
        repos = []
        while True:

            # Scrape all the repos in each page
            repos_url = user['repos_url'] + '?page=' + str(i)
            #print('repos_url', i, repos_url) 
            repos_i = requests.get(repos_url , auth=(self.username, self.token)).json()

            # Stop scraping when there is no more repos in the current page
            if len(repos_i) == 0:
                break
            
            else:
                #print(len([repo for repo in repos_i if repo['fork'] == False]))
                repos += [repo for repo in repos_i if repo['fork'] == False]
                i += 1
            

        # Scrape the information of all the repos of the user
        total_stars, forks, languages, descriptions, dates, max_star, readmes= self.find_repo_info(
            user_name, repos, contributor)

        return [user_name, name, type_user, html_url, bio, company, email, followers,
                following, hireable, location, created_at, updated_at, total_stars, max_star,
                forks, languages, descriptions, dates, readmes
            ]


    def find_repo_info(self, user_name, repos, contributor):
        '''Scrape the information of all the repos of a user

        Parameters
        ----------
        user_name: str
            Name of the owner of the repo

        repos: list
            List of response of every repo of a user

        contributor: bool
            Whether a user is the contributor of the repo 


        Attributes
        ---------
        max_star: int
            Maximum number of stars among all the repos of a user
        
        total_stars: int
            Total number of stars of all the repos of a user

        forks: int
            Total number of forks of all the repos of a user

        languages: nested list
            List of all the languages used in each repo

        dates: list
            List of the updated dates of each repo
        '''

        # Return None if user has no repo
        if len(repos) == 0:
            return None, None, None, None, None, None, None

        max_star = float('-inf')
        total_stars = 0
        forks = 0
        languages = []
        descriptions = []
        dates = []
        readmes = []

        with Bar('Extract_repo', max=len(repos)) as bar:
            for repo in repos:
                repo_info = self.get_repo(user_name, repo, contributor)
                descriptions.append(repo_info[0])
                dates.append(repo_info[1])
                languages.append(repo_info[2])
                forks += repo_info[3]
                num_stars = repo_info[4]
                total_stars += num_stars
                if max_star < num_stars:
                    max_star = num_stars
                readmes.append(repo_info[5])

                bar.next()

        #print(readmes)

        return total_stars, forks, languages, descriptions, dates, max_star, readmes

    def get_repo(self, user_name, repo, contributor):
        '''Extract information from each repo

        Parameters
        ----------
        user_name: str
            Name of the owner of the repo

        repo: dict
            Response of request of a repo's url

        contributor: bool
            Whether a user is the contributor of the repo 
        
        '''

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
        readme_url = repo['url'] + '/readme'

        readme = None

        try:
            readme = requests.get(readme_url, auth=(self.username, self.token)).json()['content']
        except:
            pass
       
        #  contributors
        if not contributor:
            try:
                contributors_url = repo['contributors_url']
                contributors_requests = requests.get(
                    contributors_url, auth=(self.username, self.token)).json()
                contributors = [contributor['login']
                                for contributor in contributors_requests if contributor['login'] != user_name]
                self.new_users += contributors
                self.new_users = list(set(self.new_users))

                # Save the contributions of users
                self.top_repo_contributions = Counter(self.top_repo_contributions) + Counter(
                    {contributor['login']: contributor['contributions'] for contributor in contributors_requests})

            except:
                pass

        return [description, updated_at, language, forks, num_stars, readme]



    def extract_contributions(self, url):
        '''Extract the contributions in the last year of a user in the main page'''

        headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                'AppleWebKit/537.11 (KHTML, like Gecko) '
                'Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive',
                'Authorization': 'token %s' % self.token}

        req= urllib.request.Request(url=url, headers=headers)
        source= urllib.request.urlopen(req).read()

        soup= BeautifulSoup(source, 'lxml')

        contribution= soup.find_all('h2', class_='f4 text-normal mb-2')[0].text

        print(int(re.findall('\d+', contribution)[0]))

        return int(re.findall('\d+', contribution)[0])

if __name__=='__main__':

    file_name = 'urls.json'

    token = dp.Variable.get(name='github_token').value
    
    username = dp.Variable.get(name='authenticated_user').value

    g = Github(token)

    user_info = GithubUserScrape(file_name, username, token, scrape_owner=False, continue_scraping=True)

    user_info.scrape()


