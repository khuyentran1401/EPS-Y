
import scrapy
import json_lines
import json
from scrapy.utils.response import open_in_browser
from scrapy.http import FormRequest
import re
import pickle

class ContributionSpider(scrapy.Spider):
    name = 'contribution'
    allowed_domains = ["github.com"]

    def start_request(self):
        profile = pickle.load(open('profile_df', 'rb'))
        urls = list(profile.html_urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        contribution = response.xpath("// h2[@class='f4 text-normal mb-2']/text()").get()
        re.findall("\d+", text)
class ProfileSpider(scrapy.Spider):
    name = "profile"
    allowed_domains = ["github.com"]
    start_urls = ['https://github.com/login']

    def parse(self, response):
        yield FormRequest.from_response(
     response,
     url='https://github.com/session',
     method="POST",
     formdata={
        'login':'myemail',
        'password':'mypassword'
     },
            callback=self.login)

    def login(self, response):

        with open('urls.json') as f:
            data = json.load(f)

            for url in data[0]['urls']:
                print('url', url)
                try:
                    yield scrapy.Request(url=url, callback=self.extract_user)
                except:
                    print('Cannot scrape this user')

    def extract_user(self, response):

        name = response.xpath('//span[@itemprop="name"]/text()').getall()
        username = response.xpath(
            '// span[@itemprop="additionalName"]/text()').get()
        bio = response.xpath(
            '//div[@class="p-note user-profile-bio mb-2 js-user-profile-bio"]/div/text()').get()

        try:
            email = response.xpath(
                '//li/@aria-label').get()
            email = re.findall('\S+@\S', email)
        except:
            pass
        

        yield {'name': name,
               'username': username,
               'bio': bio,
               'email': email
               }





