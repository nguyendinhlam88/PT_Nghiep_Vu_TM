import scrapy
# import requests
from scrapy.http import Request
from crawler.items import IMDBItem


class ImdbSpider(scrapy.Spider):
    name = 'imdb'
    allowed_domains = ['www.imdb.com']

    def __init__(self):
        super().__init__()
        with open('/Users/yaya/Desktop/PT_Nghiep_Vu_TM/crawler/config/imdb_genre.txt', 'r') as file:
            categories = file.readlines()
            base_url = "https://www.imdb.com/search/title/?genres="
            self.start_urls = [(base_url + category.strip())
                               for category in categories if category != '']

    def parse(self, response):
        urls = response.xpath(
            '//h3[@class="lister-item-header"]/a/@href').extract()
        for url in urls:
            absolute_path = response.urljoin(url)
            yield Request(absolute_path, callback=self.parse_movie)
        next_page = response.xpath('//a[@class="lister-page-next next-page"]/@href').extract_first()
        if next_page:
            absolute_path = response.urljoin(next_page)
            yield Request(absolute_path, callback=self.parse)

    def parse_movie(self, response):
        item = IMDBItem()
        item['title'] = response.xpath(
            '//h1[@data-testid="hero-title-block__title"]/text()').extract_first()
        item['rating'] = response.xpath(
            '//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span/text()').extract_first()
        api = f"https://caching.graphql.imdb.com/?operationName=TMD_Storyline&variables=%7B%22titleId%22%3A%22{response.url.split('/')[4]}%22%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%22cbefc9c4a2dbd0a5583e223e5bc788946016db709a731c85251fc1b1b7a1afbe%22%2C%22version%22%3A1%7D%7D"
        # content_api = requests.get(
        #     api, headers={"content-type": "application/json"}).json()
        # content_api["data"]["title"]["summaries"]["edges"]["node"]["plotText"]["plaidHtml"]
        item['plot_description'] = None
        item['budget'] = response.xpath(
            '//li[@data-testid="title-boxoffice-budget"]/div//span/text()').extract_first()
        item['box_office_gross'] = response.xpath(
            '//div[@data-testid="title-boxoffice-section"]//span['
            '@class="ipc-metadata-list-item__list-content-item"]/text()').extract_first()
        item['opening_weekend_gross'] = response.xpath(
            '//li[@data-testid="title-boxoffice-openingweekenddomestic"]/div//span/text()').extract_first()
        yield item
