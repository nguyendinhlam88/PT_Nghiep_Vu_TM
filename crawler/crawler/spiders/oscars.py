import scrapy
import uuid
from datetime import datetime


class OscarsSpider(scrapy.Spider):
    name = 'oscars'
    allowed_domains = ['oscars.org']
    base_url = "https://oscars.org/oscars/ceremonies/"
    start_urls = ['https://oscars.org/oscars/ceremonies/1929']

    def parse(self, response):
        items = response.xpath('//div[@class="view-grouping"]')
        if not items:
            return
        for item in items:
            category = item.xpath('.//h2/text()').extract_first()
            actor_names = item.xpath('.//div[contains(@class, "views-field-field-actor-name")]//h4//text()').extract()
            title_names = item.xpath('.//div[contains(@class, "views-field-title")]//span[@class="field-content"]//text()').extract()
            for key, value in dict(zip(actor_names, title_names)).items():
                yield {'id': uuid.uuid4(),
                       'created_date': datetime.now(),
                       'year': response.url.split('/')[-1],
                       'category': category,
                       'name of actor': key.strip(),
                       'name of film': value.strip(),
                       }
        next_page = self.base_url + str(int(response.url.split('/')[-1]) + 1)
        yield scrapy.Request(next_page, callback=self.parse)


