from scrape_googlescholar.scrapp_scholar import UserScrapp, PaperScrapp
from graph_algorithms.explore import Graph_explore
from scrape_googlescholar.utils import *
from scrape_kaggle.scrape import *
import json
import pickle

'''test = UserScrapp("https://scholar.google.com/citations?user=Vs-MdPcAAAAJ&hl=en&oi=sra")
test.get_cites_stats()
test.get_basic_profile_info()
test.colaborators()
test.get_papers_names()
print(test.info.keys())

print(test.info)'''


g = Graph_explore(Scrape_Kaggles, [{'id':'bestfitting', 'link':'https://www.kaggle.com/bestfitting'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()



g = Graph_explore(Scrape_Kaggles, [{'id':'wowfattie', 'link':'https://www.kaggle.com/wowfattie'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()


g = Graph_explore(Scrape_Kaggles, [{'id':'kazanova', 'link':'https://www.kaggle.com/kazanova'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()


g = Graph_explore(Scrape_Kaggles, [{'id':'philippsinger', 'link':'https://www.kaggle.com/philippsinger'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()


g = Graph_explore(Scrape_Kaggles, [{'id':'titericz', 'link':'https://www.kaggle.com/titericz'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()


g = Graph_explore(Scrape_Kaggles, [{'id':'david1013', 'link':'https://www.kaggle.com/david1013'}], levels=2, max_scrap=100, name_db = 'KaggleBD')
g.explore()
#t = EmailFind('Sammy Bengio Google', 'linkedin').search_email()


'''a = Scrape_Kaggles('https://www.kaggle.com/bestfitting')
a.get_json()'''

'''a = Scrape_Kaggles('https://www.kaggle.com/bestfitting', type_='profile')
a.explore()
print(a.info)'''

'''a = Scrape_Kaggles('https://www.kaggle.com/wowfattie')
a.get_json()

print(a.info.keys())
print(a.info['followers']['list'][0])
#print(res)
'''
'''a = Scrape_Kaggles('https://www.kaggle.com/kazanova')
a.get_json()'''



