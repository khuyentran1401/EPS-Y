import os
import urllib
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_googlescholar.utils import * 
import re
import json
from pymongo import MongoClient


class Scrape_Kaggles(object):
	"""
	Class to scrape Kaggle, this class allows to scrape from profile and from a competition
	To change from profile to competition, change type_ to 'profile' or 'competition'
	With the function explore, if to_db = True, everything will be saved into the MongoDB.
	"""
	def __init__(self, url, type_='default', max_time=1000, to_db=False, name_db = 'KaggleDB', ip_db = 'localhost', port_db = 27017):
		'''
		Initialization funtion for the kaggle scrapping funtion:
		Input: 
			url -> the Kaggle url to scrape
			type_ -> the type of url to scrape (profileñ/competition)
			to_db -> If true, with explore, the data will be stored in the DB
            name_db -> The name of the database that we want to use
            ip_db -> The ip of the database
            port_db -> The port of the database
            max_time -> Max time for each request
		'''
		super(Scrape_Kaggles, self).__init__()
		self.url = url
		self.max_time=1000
		if type_ == 'default':
			if 'c' in self.url.split('/'):
				self.type_ = 'competition'
			else:
				self.type_ = 'profile'
		else:
			self.type_ = type_
		try:
			self.html = connection(self.url, 0, max_time, time.time()).read()
		except:
			self.html = None
			print("Cannot connect to the url: " + self.url)
		self.info = {}
		

		if to_db:
			self.connection = MongoClient(ip_db, port_db)
			self.db = self.connection[name_db]
			if self.type_ == 'profile':
				self.kaggle = self.db.kaggle_profile
			else:
				self.kaggle = self.db.kaggle_comp
		else:
			self.connection = None
			self.db = None
			self.kaggle = None


	def get_json(self):
		if self.html == None:
			print('No file found')
			return -1


		information = []

		exp = re.compile('Kaggle.State.push\((.+?)\)\;')
		res = exp.findall(str(self.html))[1]


		regex = re.compile(r'\\(?![/u"])')
		fixed = regex.sub(r"\\\\", res)
		try:
			self.info =  json.loads(fixed)
		except:
			print("Error found while extracting the info from the json")
			return -1


	def get_colaborators(self):
		if self.info == {}:
			self.get_json()
		#self.info['followers']['list']

		ret = []
		if self.type_ == 'profile':
			for i in self.info['followers']['list']:
				aux = {}
				aux['id'] = i['userUrl'][1:]
				aux['link'] = 'https://www.kaggle.com' + i['userUrl']
				ret.append(aux)

			for i in self.info['followers']['list']:
				aux = {}
				aux['id'] = i['userUrl'][1:]
				aux['link'] = 'https://www.kaggle.com' + i['userUrl']
				ret.append(aux)

		elif self.type_ == 'competition':
			for i in range(self.info['discussionTeaser']):
				aux = {}
				aux['id'] = i['userUrl'][1:]
				aux['link'] = 'https://www.kaggle.com' + i['userUrl']
				ret.append(aux)

			for i in range(self.info['kernelTeaser']):
				aux = {}
				aux['id'] = i['userUrl'][1:]
				aux['link'] = 'https://www.kaggle.com' + i['userUrl']
				ret.append(aux)

		return ret


	def explore(self):
		if self.html:
			if self.get_json() == -1:
				print("Error with the json")
				return False
			if self.kaggle:
				self.kaggle.insert_one(self.info)
			return True
		print("Not able to read HTML file")
		return False