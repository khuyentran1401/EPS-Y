from scrapp.scrapp_scholar import UserScrapp, PaperScrapp

test = UserScrapp("https://scholar.google.com/citations?user=Vs-MdPcAAAAJ&hl=en&oi=sra")
test.get_cites_stats()
test.get_basic_profile_info()
test.get_colaborators()
test.get_papers_names()
print(test.info.keys())

#print(test.info)

test_papers =  PaperScrapp(test.info['papers'])
test_papers.explore_papers(store_path='papers/')



test = UserScrapp("https://scholar.google.com/citations?user=Vs-MdPcAAAAJ&hl=en&oi=sra")
test.get_cites_stats()
