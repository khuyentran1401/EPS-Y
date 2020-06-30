import os
import urllib
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import urlopen
from scrape_googlescholar.utils import * 
from scrape_kaggle.utils import *
import re
import json


class Scrape_Kaggles(object):
	"""
	Class to scrape Kaggle, this class allows to scrape from profile and from a competition
	To change from profile to competition, change type_ to 'profile' or 'competition'
	With the function explore, if to_db = True, everything will be saved into the MongoDB.
	"""
	def __init__(self, url, type_='profile', max_time=1000, to_db=False, name_db = 'KaggleDB', ip_db = 'localhost', port_db = 27017):
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
		self.type_ = type_
		self.max_time=1000
		try:
			self.html = connection(self.url, 0, max_time, time.time()).read()
		except:
			self.html = None
			print("Cannot connect to the url: " + self.url)
		self.info = {}


	def get_json(self):
		if self.html == None:
			print('No file found')
			return -1
		information = []
		aux = str(self.html).split(';')
		for i in aux:
			if "Kaggle.State.push" in i:
				information.append(i)

		#try to get json, but I get an encoding error
		res = information[1][18:-1]
		regex = re.compile(r'\\(?![/u"])')
		fixed = regex.sub(r"\\\\", res)

		return json.loads(fixed)

