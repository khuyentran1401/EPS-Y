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

    html = urlopen(commit_link)
    soup = BeautifulSoup(html, 'html.parser')


    #Extract all commits
    commits = soup.find_all(
        'a', class_='commit-author tooltipped tooltipped-s user-mention')
    for commit in commits:
        if commit.text == username:
            author_commit = commit['href']
            break

    author_commit = 'https://github.com' + author_commit
    html = urlopen(author_commit)
    soup = BeautifulSoup(html, 'html.parser')

    author_commit_link = soup.find(
        'a', class_="message js-navigation-open")['href']
    author_commit_link = 'https://github.com' + author_commit_link + '.patch'

    html = urlopen(author_commit_link)
    soup = BeautifulSoup(html, 'html.parser')

    email = soup.prettify().split()[-1]
    # Clean email address
    email = re.sub('[</>]', '', email)

    return email



if __name__=='__main__':
    username = sys.argv[1]
    print(extract_email(username))


