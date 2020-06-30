from scrape_googlescholar.scrapp_scholar import UserScrapp, PaperScrapp
from graph_algorithms.explore import Graph_explore
from scrape_googlescholar.utils import *
from scrape_kaggle.scrape import *


'''test = UserScrapp("https://scholar.google.com/citations?user=Vs-MdPcAAAAJ&hl=en&oi=sra")
test.get_cites_stats()
test.get_basic_profile_info()
test.colaborators()
test.get_papers_names()
print(test.info.keys())

print(test.info)'''


#g = Graph_explore(UserScrapp, [{'id':'Vs-MdPcAAAAJ&hl', 'link':'https://scholar.google.com/citations?user=Vs-MdPcAAAAJ&hl=en&oi=sra'}], levels=2, max_scrap=100)
#g.explore()

#t = EmailFind('Sammy Bengio Google', 'linkedin').search_email()


'''a = Scrape_Kaggles('https://www.kaggle.com/bestfitting')
a.get_json()'''

a = Scrape_Kaggles('https://www.kaggle.com/wowfattie')
a.get_json()

'''a = Scrape_Kaggles('https://www.kaggle.com/kazanova')
a.get_json()'''