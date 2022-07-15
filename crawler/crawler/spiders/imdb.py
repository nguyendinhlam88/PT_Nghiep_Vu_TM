import scrapy
import os
import re

os.chdir(os.getcwd())

import requests
import uuid

from datetime import datetime
from scrapy.http import Request


# from crawler.items import IMDBItem


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com', 'caching.graphql.imdb.com']

    def __init__(self):
        super().__init__()
        with open(os.getcwd() + '/config/imdb_genre.txt', 'r') as file:
            categories = file.readlines()
            base_url = "https://www.imdb.com/search/title/?year=2000-01-01,&boxoffice_gross_us=0.0,&genres={}&sort=year,asc"
            self.start_urls = [base_url.format(category.strip())
                               for category in categories if category != '']
        current_genre = None

    def parse(self, response):
        min, max = re.search(r'genres=.*&', response.url).span()
        genre = response.url[min + 7:max - 1].split('&')[0]
        movies = response.xpath(
            '//h3[@class="lister-item-header"]')
        for movie in movies:
            url = movie.xpath('.//a/@href').extract_first()
            year = movie.xpath('.//span[@class="lister-item-year text-muted unbold"]//text()').extract_first()
            year = re.search(r'\d{4}', year).group()
            absolute_path = response.urljoin(url)
            yield Request(absolute_path, callback=self.parse_movie, cb_kwargs={'genre': genre, 'year': year})
        next_page = response.xpath('//a[@class="lister-page-next next-page"]/@href').extract_first()
        if next_page:
            absolute_path = response.urljoin(next_page)
            yield Request(absolute_path, callback=self.parse)

    def parse_movie(self, response, genre, year):
        item = {}
        item['id'] = str(uuid.uuid4())
        item['url'] = response.url
        item['created_date'] = datetime.now()
        item['genre'] = genre
        item['year'] = year
        item['title'] = response.xpath(
            '//h1[@data-testid="hero-title-block__title"]/text()').extract_first()
        item['rating'] = response.xpath(
            '//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span/text()').extract_first()
        api = f"https://caching.graphql.imdb.com/?operationName=TMD_Storyline&variables=%7B%22titleId%22%3A%22{response.url.split('/')[4]}%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%22cbefc9c4a2dbd0a5583e223e5bc788946016db709a731c85251fc1b1b7a1afbe%22%2C%22version%22%3A1%7D%7D"
        content_api = requests.get(api, headers={"content-type": "application/json"}).json()
        item['plot_description'] = content_api["data"]["title"]["summaries"]["edges"][0]["node"]["plotText"][
            "plaidHtml"] if content_api["data"]["title"]["summaries"]["edges"] else None
        item['budget'] = response.xpath(
            '//li[@data-testid="title-boxoffice-budget"]/div//span/text()').extract_first()
        item['box_office_gross'] = response.xpath(
            '//li[@data-testid="title-boxoffice-cumulativeworldwidegross"]/div//span/text()').extract_first()
        item['opening_weekend_gross'] = response.xpath(
            '//li[@data-testid="title-boxoffice-openingweekenddomestic"]/div//span/text()').extract_first()
        yield item
