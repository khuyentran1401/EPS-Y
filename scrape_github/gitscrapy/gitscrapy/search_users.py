'''Find the info of git users'''



import requests
from pprint import pprint
import base64
from extract_datapoint import get_repo, extract_profile, extract_contributions
from github import Github
import json

import pandas as pd
import numpy as np
import datapane as dp

from progress.bar import Bar
import pickle

import time
import re
from bs4 import BeautifulSoup
import urllib.request


def find_repo_list():    
    ''' Find urls and repo's names to extract '''

    repos = []

    with open('urls.json') as f:
        data = json.load(f)
        with Bar('Extract_repo_list', max = len(data)) as bar:
            for page in data:
                repos += page['repo_name']
                bar.next()

    return repos


def user_info(repos, g):
    '''Get information about the repo and find contributors'''
    info = []
    new_users = []

    with Bar('Extract_user_info', max=len(repos)) as bar:
        for i, repo in enumerate(repos):
            user = repo.split('/')[0]
            print('\n',i, user)

            url = 'https://api.github.com/users/' + user
            print('url')
            user = requests.get(url).json()

            # Exclude origanization
            if user['type'] == 'User':
                user_info = extract_profile(user, g, new_users)     
                info.append(user_info)
            else:
                print('pass')
                pass
            bar.next()

    pickle.dump(info, open("owner_info", 'wb'))

    # get unique users
    new_users = list(set(new_users))

    with Bar('Extract_contributor_info', max=len(new_users)) as bar:
        for user in new_users:
            contributor_info = extract_profile(user, g, new_users, contributor=True)
            info.append(contributor_info)

            bar.next()

     
    # Create dataframe to hold new information
    repo_df = pd.DataFrame(np.array(info), columns=['user_name', 'name', 'type_user', 'html_url', 'bio', 'company', 'email', 'followers',
                                                    'following', 'hireable', 'location', 'created_at', 'updated_at', 
                                                    'total_stars', 'max_star', 'forks', 'languages', 'descriptions', 'dates'])


    return repo_df 

def contributions_info(df):

    urls = list(df.html_url)

    print(len(urls))
    contributions = []
    exceptions = []

    with Bar('Extract_contributions', max=len(urls)) as bar:

        for url in urls:
            time.sleep(5)
            try:
                contribution = extract_contributions(url)
                contributions.append(contribution)
            except:
                exceptions.append(url)
            
            bar.next()

    return contributions, exceptions 

def merge_df(contributions, exceptions, df):

    # Find the indices of users to exclude
    exclude_ind = []

    for i, url in enumerate(df.html_url):
        if url in exceptions:
            exclude_ind.append(i)

    # Remove the users without the contributions
    df = df[~df.index.isin(exclude_ind)]

    df = df.reset_index().drop('index', axis=1, inplace=True)

    df['contribution'] = contributions 

    return df 


        


if __name__=='__main__':

    token = dp.Variable.get(name='github_token')
    token = token.value
    g = Github(token)
    repos = find_repo_list()
    profile_df = user_info(repos, g)
    #profile_df = pickle.load(open('profile_df', 'rb'))
    pickle.dump(profile_df, open("profile_df", 'wb'))

    #print(profile_df.info())

    #contributions, exceptions = contributions_info(profile_df)

    #new_df = merge_df(contributions, exceptions, profile_df)

    # Save the df and new_users 
    #pickle.dump(new_df, open("profile_df_extension", 'wb'))




        


