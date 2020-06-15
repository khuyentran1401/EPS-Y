from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
import scrapy



class LoginSpider(scrapy.Spider):
    name = "login2"

    start_urls = ('http://quotes.toscrape.com/login',)

    def parse(self, response):
        open_in_browser(response)
        token = response.xpath('//*[@name="csrf_token"]/@value').extract_first()

        return FormRequest.from_response(response,
                                        formdata={
                                            'csrf_token':token,
                                            'password': 'foobar',
                                            'username' : 'foobar'},
                                        callback=self.scrape_pages)
    def scrape_pages(self, response):
        yield {name:'Khuyen'}
