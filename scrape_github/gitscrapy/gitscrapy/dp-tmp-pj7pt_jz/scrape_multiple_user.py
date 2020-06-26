import scrapy
import json_lines
import json
from scrapy.utils.response import open_in_browser
from scrapy.http import FormRequest
import re


class FindUser(scrapy.Spider):

    def __init__(self):
        self.num_page = 0
    name = "find_user"
    allowed_domains = ["github.com"]
   
    start_urls = ['https://github.com/search?q=machine+learning&type=Repositories']


    def parse(self, response):

        # Find urls under machine learning search in tab Repositories
        repos = response.xpath('//div[@class="f4 text-normal"]/a/@href').getall()
        repo_urls = []
        for i, repo in enumerate(repos):
            #url = url.split("/")[1]
            repo_urls.append('https://github.com' + repo)
            repos[i] = repo[1:]

        print(repo_urls)
        
        yield {'url': repo_urls,
        'repo_name': repos}

        next_page = response.css('a.next_page::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            self.num_page += 1
            yield scrapy.Request(next_page, callback=self.parse)
        
