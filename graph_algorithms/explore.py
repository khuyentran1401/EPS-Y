import os


'''
To do:
    Add some exception to handle incomplete process, when ctrl + c is pressed.
    We can save the current queue and the restar from it.
'''



class Graph_explore(object):
    '''
    Algorithm based on BFS and DFS algothms to explore the graph created by the people and
    their coauthors in Google Scholar, GitHub and Kaggle.

    The scrape classes of Google Scholar, GitHub and Kaggle must have the method .get_colaborators()
    This method should return a list of dicctionaries, where one of the keys is 'link'.
    '''

    def __init__(self, scraper, inits, levels=None, max_scrap=None, type_exp='BFS', to_db = True, name_db = 'ScholarDB', ip_db = 'localhost',  port_db=27017, max_time=1000):
        '''
        Init function of the graph exploration data structure.
        Input:
            -> scraper: The data structure that will be used to explore the graph (i.e. GitHub, Scholar, Kaggle)
            -> inits: A list og the initial points to explore (i.e. A list of links)
            -> levels: The number of levels, if None, there will be no limit
            -> max_scrap: The algorithm will end when this number is archieved.
            -> type_exp: BFS or DFS to explore the graph
            -> to_db: If true, the exploration will be saved in to the Database
            -> mane_db: The name of the Database to use
            -> ip_db: The ip where the database is located
            -> port_db: The port to the Database
            -> max_time: The max time to have an answer in each request
        '''
        self.scraper = scraper
        self.inits = inits
        self.type_exp= type_exp
        self.to_db = to_db
        self.name_db = name_db
        self.ip_db = ip_db
        self.port_db = port_db
        self.max_time = max_time
        if levels:
            self.levels = levels
        else:
            self.levels = None
        if max_scrap:
            self.max_scrap = max_scrap
        else:
            self.max_scrap = float('inf')


    def explore(self):
        '''
        Functiuon to star the exploration of the graph. This will handle the failures in connection.
        '''
        queue = [(i, 0) for i in self.inits]
        visited = set()
        while len(queue) > 0 and len(visited) < self.max_scrap:
            print("Trying again with failed nodes")
            queue, visited = self.explore_util(queue)


    def explore_util(self, queue = None, visited = None):
        '''
        This function is tries to explore the graph with the selected algorithm.
        Input:
            queue ->  the current queue of the nodes to explore
            visited ->  a set of the visited nodes
        Output:
            fialed -> the nodes that failed to explore
            visited -> the visited nodes so far.

        Note:
            A node is considered visited, when it has been saved into the DataBase.
        '''
        if queue == None:
            queue = [(i, 0) for i in self.inits]
        if visited == None:
            visited = set()
        failed = []
        while len(queue) > 0 and len(visited) < self.max_scrap:
            cur_node = queue.pop(0)
            print("------------")
            print(cur_node)
            print("------------")
            if cur_node[0]['id'] in visited: #in case this node has been visited
                continue
            visited.add(cur_node[0]['id'])
            cur = self.scraper(cur_node[0]['link'], to_db = self.to_db, name_db = self.name_db, ip_db = self.ip_db,  port_db=self.port_db, max_time=self.max_time)
            ans = cur.explore()
            if ans == False:
                print("Saving link for later because of connection failure")
                failed.append(cur_node)
                continue
            visited.add(cur_node[0]['id'])
            if cur_node[1] > self.levels: ##in case the max depth was reaches
                continue
            if self.type_exp == "BFS":
                queue = queue + [(i, cur_node[1]+1) for i in cur.get_colaborators()]
            else:
                queue = [(i, cur_node[1]+1) for i in cur.get_colaborators()] + queue
            print("Node explored")
        return failed, visited

