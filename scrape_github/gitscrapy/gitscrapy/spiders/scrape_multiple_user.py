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

    start_urls = [
        'https://github.com/search?p=1&q=machine+learning&type=Users']

    def parse(self, response):
        #repo_urls = response.xpath('// li[@class="repo-list-item hx_hit-repo d-flex flex-justify-start py-4 public source"]/div[2]/div/a/@href').getall()
        repo_urls = response.xpath('// a[@class="mr-1"]/@href').getall()
        for i, url in enumerate(repo_urls):
            #url = url.split("/")[1]
            repo_urls[i] = 'https://github.com' + url

        yield {'page %s' % str(self.num_page): repo_urls}

        next_page = response.css('a.next_page::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            self.num_page += 1
            yield scrapy.Request(next_page, callback=self.parse)
