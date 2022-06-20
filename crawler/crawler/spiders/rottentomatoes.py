import scrapy
import uuid
import re
from datetime import datetime


class RottentomatoesSpider(scrapy.Spider):
    name = 'rottentomatoes'
    allowed_domains = ['www.rottentomatoes.com']
    start_urls = ['https://www.rottentomatoes.com/browse/movies_in_theaters/?page=1',
                  'https://www.rottentomatoes.com/browse/movies_at_home/?page=1']
    last_url = None

    def parse(self, response):
        current_page_urls = response.xpath('//div[@class="discovery-tiles__wrap"]/a/@href').extract()
        if self.last_url == current_page_urls[-1]:
            return
        for url in current_page_urls:
            absolute_path = response.urljoin(url)
            yield scrapy.Request(absolute_path, callback=self.parse_movie)
        self.last_url = current_page_urls[-1]
        current_page = int(response.url.split('=')[-1])
        next_page = current_page + 1
        next_url = response.url.replace(str(current_page), str(next_page))
        yield scrapy.Request(next_url, callback=self.parse)

    def parse_movie(self, response):
        item = {}
        item['id'] = uuid.uuid4()
        item['url'] = response.url
        item['created_date'] = datetime.now()
        tmp1 = response.xpath('//score-board//@tomatometerscore').extract_first()
        item['critic_score'] = tmp1 + '%' if tmp1 else None
        tmp2 = response.xpath('//score-board//@audiencescore').extract_first()
        item['audience_score'] = tmp2 + '%' if tmp2 else None

        # Thông tin item trong danh sách mô tả
        keys = response.xpath('//div[@data-qa="movie-info-item-label"]//text()').extract()
        keys = [key.replace(':', '') for key in keys]
        values = response.xpath('//div[contains(@class, "meta-value")]')
        values_cleaned = []
        for value in values:
            value = value.xpath('.//text()').extract()
            if len(value) > 1:
                value = ' '.join([item.replace('\n', ' ').strip() for item in value]).strip()
            else:
                value = value[0].replace('\n', ' ').strip()
            value = re.sub(r'\s+', ' ', value)
            values_cleaned.append(value)
        item_attributes = dict(zip(keys, values_cleaned))

        item['runtime'] = item_attributes['Runtime'] if 'Runtime' in item_attributes else None
        item['MPAA_rating'] = item_attributes['Rating'] if 'Rating' in item_attributes else None
        item['studio'] = item_attributes['Distributor'] if 'Distributor' in item_attributes else None
        item['theater_release_date'] = item_attributes['Release Date (Theaters)'] if 'Release Date (Theaters)' in item_attributes else None
        item['DVD_release_date'] = item_attributes['Release Date (Streaming)'] if 'Release Date (Streaming)' in item_attributes else None
        item['list_of_genres'] = item_attributes['Genre'] if 'Genre' in item_attributes else None
        item['abridged_list_of_cast'] = ', '.join([item.replace('\n', ' ').strip() for item in response.xpath('//div[@class="cast-item media inlineBlock  "]//a//span//text()').extract()])
        item['abridged_list_of_directors'] = item_attributes['Director'] if 'Director' in item_attributes else None
        return item

