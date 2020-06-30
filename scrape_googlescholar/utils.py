from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from urllib import request
import urllib
import time
import re


def connection(url, level = 0, max_time = 1000, init_time = None):
    '''
    Function to handle the requests
    Input:
        -> url: the url to get
        -> level: The request level
        -> max_time: The maximum time to get the request
        -> init_time: The time when the request started
    '''
    if init_time == None:
        init_time = time.time()
    if time.time() - init_time > max_time:
        print("Request exceded the maxtime")
        return -1
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
        req = urllib.request.Request(url, headers=headers)
        r = urllib.request.urlopen(req)
        time.sleep(5)
    except:
        print("Error found, wait to the next request")
        time.sleep(5)
        return connection(url, level + 1, max_time, init_time)
    return r



def get_email(url, max_time=1000):
	'''
	This funciton searchs for the email on the personal web pager. To search the email we search for @ and the mords email in the class or 
	id form the objects in the html file.
	Input:
		-> url: the url of the webpage we want to explore
		-> maxtime: the maxtime to get the webpage
	'''
	try:
		html = BeautifulSoup(connection(url, 0, max_time, time.time()), features='html.parser')
	except:
		print("Cannot connect to the url: ", url)
		return -1
	aux = str(html).split('<')
	cads = []
	for cad in aux:
		cads += cad.split('>')
	emails = [e for e in cads if (re.search("@", e) or re.search("\[at\]", e) or re.search("\[AT\]", e)) and len(e) < 100 and ('(' not in e or ')' not in e)]
	if len(emails) == 0:
		return -1
	return emails




class EmailFind(object):
	"""
	This data structure helps tp extracte the emails from the researchers by making a google search
	It looks for the top links on the google search to get the email.
	"""
	def __init__(self, link, type_='link', max_time=10):
		'''
		Funciotn to initialize the data structure
		Input:
			-> link: the link or keywords to make the search
			-> type: link, linkedin, or kwds. If link, the the link will be used to make the search. If kwds, 
						it will make a google search with the kwds given.
			-> max_time_ the maxtime to make the requests
		'''
		super(EmailFind, self).__init__()
		self.max_time = max_time
		self.type_ = type_
		if type_ == 'link':
			self.link = link			
		else:
			aux = ""
			cont = 0
			for i in link.split():
				aux += i.lower()
				if cont < len(link.split())-1:
					aux += '+'
				cont += 1
			#the linkedin search.
			if type_ == 'linkedin':
				aux += '+linkedin'
			self.link = "https://www.google.com/search?rls=en&q=" + aux + "&ie=UTF-8&oe=UTF-8"


		try:
			self.html = BeautifulSoup(connection(self.link, 0, self.max_time, time.time()).read(), features='html.parser')
		except:
			self.html = None
			print("Cannot open the url: " + self.link)


		self.explore_links = []
		self.emails = []
		
	def get_links(self, n=5):
		'''
		Function to get the links from the google search, if the type of search is linkedin, just we will
		just considef LinkedIn urls.
		Input:
			-> n: the number of links to extract
		'''
		cont = 0
		for i in self.html.find_all(class_='g'):
			if cont >= n:
				break
			if self.type_ == 'linkedin':
				if 'linkedin' not in i.a['href'].split('.'):
					continue
			if re.search("ieeexplore", i.a['href']):
				continue
			self.explore_links.append(i.a['href'])
			cont += 1


	def search_email(self):
		'''
		This funciton runs the function to search an email on the links selected. If the search is of
		LinkedIn, then the function get_linkedin_emails will be called.
		'''
		if self.explore_links == []:
			print("No links to explore, getting links")
			self.get_links()

		if self.type_ == 'linkedin':
			self.get_linkedin_emails()
			print(self.emails)
			return

		for i in self.explore_links:
			try:
				aux = get_email(i, self.max_time)
				if aux == -1:
					continue
				self.emails+=aux

			except:
				print("Cannot get an email from the url: ", i)
		print(self.emails)



	def get_linkedin_emails(self):
		print(self.explore_links)




