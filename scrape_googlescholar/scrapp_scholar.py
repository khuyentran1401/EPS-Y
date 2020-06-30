from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError
from urllib import request
from fp.fp import FreeProxy
import urllib
import time
import random as rand
from pymongo import MongoClient
from scrape_googlescholar.utils import *



class UserScrapp(object):
    '''
    Class to scrapp Google Scholar
    Scrapp by:
        -Profile
    '''
    def __init__(self, url, type='profile', to_db = False, name_db = 'ScholarDB', ip_db = 'localhost',  port_db=27017, max_time=1000):
        '''
        Initialization function for the Scholar Scrapping class
        Input:
            url -> the Google Scholar url to scrapp
            type -> the type of link we have
            to_db -> If true, with explore, the data will be stored in the DB
            name_db -> The name of the database that we want to use
            ip_db -> The ip of the database
            port_db -> The port of the database
            max_time -> Max time for each request
        '''
        self.url = url
        try:
            self.html = BeautifulSoup(connection(self.url, 0, max_time, time.time()).read(), features='html.parser')
        except:
            self.html = None
            print("Cannot connect to the url: " + url)
        self.type = 'profile'
        self.info = {'google_user_id':self.url.split('&')[0].split('?')[1].split('=')[1]}
        #maybe we should asign some id to link the people form the working network

        #connection to the database
        if to_db:
            self.connection = MongoClient(ip_db, port_db)
            self.db = self.connection[name_db]
            self.scholar = self.db.scholar
        else:
            self.connection = None
            self.db = None
            self.scholar = None


    def get_basic_profile_info(self):
        '''
        Function to get the basic profile info, that is name, work, personal webpage if any and tags
        '''
        prof = self.html.find(id='gsc_prf_i')
        cont = 0
        labels = ['name', 'work', 'personal_web', 'tags']
        self.info['profile'] = {}
        for i in prof:
            if cont == 2:
                try:
                    self.info['profile'][labels[cont]] = i.a['href']
                except:
                    print("No personal web found")
                cont += 1
                continue
            if cont == 3:
                self.info['profile'][labels[cont]] = []
                for j in i:
                    self.info['profile'][labels[cont]].append(j.get_text())
                cont += 1
                continue
            self.info['profile'][labels[cont]] = i.get_text()
            cont += 1


    def get_cites_stats(self):
        '''
        Function to get the basic citation information from a profile in Google Scholar
        the information retreived is:
                    All     Since 2015
        Citations    x          x
        h-index      x          x
        i10-index    x          x
        '''
        table = self.html.find(id="gsc_rsb_st")
        headers = []
        self.info['citation'] = {}
        for i in table.thead.tr:
            if i.get_text == '':
                continue
            headers.append(i.get_text())


        for i in table.tbody.find_all('tr'):
            cont = 0
            for j in i.find_all('td'):
                if cont == 0:
                    name = j.get_text()
                    self.info['citation'][name] = {}
                    cont+=1
                    continue
                self.info['citation'][name][headers[cont]] = j.get_text()
                cont += 1

    def colaborators(self):
        '''
        Funtion to get the colaborators of a person
        ########A modification of this function may be used to crate an exploration tree
        Gets the names of the top 20 colaborators (Should be improved to get all the colaborators)
        '''
        colab = self.html.find(id='gsc_rsb_co')
        self.info['colab'] = []
        try:
            for i in colab.ul:
                self.info['colab'].append(i.a['href'].split('&')[0].split('?')[1].split('=')[1])
        except:
            print("No colaborators found")

    def get_papers_names(self):
        '''
        Get the basic information of the papers, all the other information can be retreived
        by using the link of the basic information of the paper
        '''
        table = self.html.find(id='gsc_a_t')
        headers = []
        self.info['papers'] = []
        #headers = set() #we might need to use a set if there is some repeated data in the future
        for i in table.thead.find_all(class_=['gsc_a_a', 'gs_nph']):
            headers.append(i.get_text())

        #to get extra information if relevant
        #info_headers = ['title', 'authors', 'published']
        for i in table.tbody.find_all('tr'):
            cont = 0
            aux = {}
            for j in i.find_all('td'):
                if cont == 0:
                    ind = 0
                    aux['title'] = j.a.get_text()
                    aux['link'] = j.a['data-href']
                    ############
                    #this is to get xetra information of the coauthors and where it was published
                    #for k in j
                    #    aux[info_headers[ind]] = k.get_text()
                    #    ind += 1
                    ###########
                    cont+=1
                    continue
                aux[headers[cont]] = j.get_text()
                cont += 1
            self.info['papers'].append(aux)

    def get_colaborators(self):
        '''
        Returns the colaborators of the current person.
        '''
        ret = []
        for colab in self.info['colab']:
            aux = {}
            aux['link'] = 'https://scholar.google.com/citations?user=' + colab + '&hl=en&oi=sra'
            aux['id'] = colab
            ret += [aux]
        return ret


    def get_id(self):
        '''
        Returns the id of the researcher
        '''
        return self.info['google_user_id']

    def explore(self):
        '''
        This function extracts all the information from the users. 
        '''
        if self.html:
            self.get_basic_profile_info()
            self.get_cites_stats()
            self.colaborators()
            self.get_papers_names()
            if self.scholar:
                self.scholar.insert_one(self.info)
            return True
        print("Not able to read HTML file")
        return False









class PaperScrapp(object):
    '''
    Class to scrapp Google scholar
    Scrapp by:
        -Papers
    '''

    def __init__(self, papers, store_path='', cur_papers = {}, cur_papers_names=set()):
        '''
            This class will recieve the reference to differente papers, just the link is needed
            Input:
                papers-> A list of strings with the links of the papers or a list of dicctionaries with all the information of the papers
                store_path -> the path where the text of the abstracts will be stored.
                cur_papers -> a set of papers scrapped before.
        '''
        if type(papers) != list:
            raise Exception("A list is needed, not type " + str(type(papers)))
        if len(papers) == 0:
            self.papers = set()
        else:
            if type(papers[0]) == str:
                self.papers = set(papers)
            else:
                try:
                    self.papers = set([papers[i]['link'] for i in range(len(papers))])
                except:
                    raise Exception("The paper info is not in the correct format, no link found")
        self.store_path = store_path
        self.cur_papers = cur_papers
        self.cur_papers_names = cur_papers_names


    def add_papers_to_explore(self, papers):
        '''
            This funciton adds new papers to scrapp
            Input:
                papers -> A list of strings with the links of the papers or a list of dicctionaries with all the information of the papers
        '''
        if type(papers) != list:
            raise Exception("Must have a list")
        if len(papers) == 0:
            return
        if tyep(papres[0]) == str:
            self.papers |= set(papers)
        else:
            try:
                 self.papers |= set([papers[i]['link'] for i in range(len(papers))])
            except:
                raise Exception("The paper insfo is not in the correct format, no link found")

    def explore_papers(self, base_url='https://scholar.google.com', store_path='/'):
        '''
            This funtions takes the information of the papers. It gets the name of the paper, the authors, where it was published
            and the abstract of the paper. All this is stored into a .txt file with the names of the paper.
        '''
        if len(self.papers) == 0:
            print("No papers to scrapp")
            return

        not_explored = []

        for i in self.papers:
            try:
                page = BeautifulSoup(connection(base_url+i).read(), features='html.parser')
                title = page.find(id='gsc_vcd_title').a.get_text()
                if title in self.cur_papers_names:
                    continue
                self.cur_papers_names.add(title)
                self.cur_papers[title] = {}
                self.cur_papers[title]['authors'] = page.find(class_='gsc_vcd_value').get_text().split(',')
                abstract = page.find(class_=['gsh_csp', 'gsh_small'])
                with open(store_path + title + 'txt', 'w') as f:
                    f.write(abstract.get_text())
                    f.close()
            except:
                not_explored.append(i)





