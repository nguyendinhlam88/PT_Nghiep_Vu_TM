import os

import scrapy
import re


class GoldenglobesSpider(scrapy.Spider):
    name = 'goldenglobes_data'
    allowed_domains = ['en.wikipedia.org']
    start_urls = ['http://en.wikipedia.org/']

    def __init__(self):
        super().__init__()
        with open(os.getcwd() + '/config/wikipedia.txt', 'r') as file:
            self.start_urls = [file.readlines()[4]]

    def parse(self, response):
        year_tables = response.xpath('//table[contains(@class, "wikitable")]')
        for table in year_tables:
            rows = table.xpath('.//tr')[1:]
            year = None
            film = None
            for row in rows:
                temp = row.xpath('.//text()').extract()
                attributes = []
                for tmp in temp:
                    tmp = tmp.strip()
                    if not tmp or tmp[0] == '[' or len(tmp) < 2:
                        continue
                    else:
                        attributes.append(tmp)
                if 'director' in response.url.lower():
                    if len(attributes) == 3:
                        year = attributes[0]
                        yield {'year': attributes[0], 'nominees': attributes[1], 'film': attributes[2], 'win': True}
                    else:
                        yield {'year': year, 'nominees': attributes[0], 'film': attributes[0], 'win': False}
                elif 'actor' in response.url.lower() or 'actress' in response.url.lower():
                    if len(attributes) == 4:
                        year = attributes[0]
                        yield {'year': attributes[0], 'actor': attributes[1], 'character': attributes[2],
                               'film': attributes[3], 'win': True}
                    elif len(attributes) == 3:
                        film = attributes[2]
                        yield {'year': year, 'actor': attributes[0], 'character': attributes[1], 'film': film,
                               'win': False}
                    elif len(attributes) == 2:
                        yield {'year': year, 'actor': attributes[0], 'character': attributes[1], 'film': film,
                               'win': False}
                else:
                    pass
