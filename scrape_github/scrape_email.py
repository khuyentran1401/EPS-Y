# Getting Started

import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from urllib.request import urlopen
import sys
import re

def extract_email(username):

    url = 'https://github.com/' + username

    html = urlopen(url)

    soup = BeautifulSoup(html, 'html.parser')

    # Go to the repo

    source_repo = soup.find('a', class_="UnderlineNav-item mr-0 mr-md-1 mr-lg-3")

    name = source_repo['href']

    # Go to the repo tab
    repo_link = 'https://github.com' + name

    # Go to type tab

    html = urlopen(repo_link + '&q=&type=source&language=')

    soup = BeautifulSoup(html, 'html.parser')

    first_repo = soup.find_all('h3')[3]

    repo_link1 = 'https://github.com' + first_repo.a['href']

    commit_link = repo_link1 + '/commits/master'
    print(commit_link)

    html = urlopen(commit_link)
    soup = BeautifulSoup(html, 'html.parser')


    #Extract commit that has the author
    commits = soup.find_all('div', class_="flex-auto min-width-0")
    print(commits)
    for commit in commits:
        if commit.div.find_all('div')[-1].text.split('\n')[1] == 'khuyentran1401':
            author_commit = commit.p.a['href']
            break
 
    author_commit = 'https://github.com' + author_commit + '.patch'


    html = urlopen(author_commit)
    soup = BeautifulSoup(html, 'html.parser')

    email = soup.prettify().split()[9]
    # Clean email address
    email = re.sub('[</>]', '', email)

    return email



if __name__=='__main__':
    username = sys.argv[1]
    print(extract_email(username))


