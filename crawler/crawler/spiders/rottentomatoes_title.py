import scrapy
import pandas as pd
import re
import uuid
from datetime import datetime


class RottentomatoesTitleSpider(scrapy.Spider):
    name = 'rottentomatoes_title'
    allowed_domains = ['www.rottentomatoes.com']
    imdb_film = pd.read_csv('/Users/yaya/Downloads/PT_Nghiep_Vu_TM/crawler/imdb.csv')
    start_urls = imdb_film.apply(
        lambda item: f'https://www.rottentomatoes.com/search?search={item["title"]} ({item["year"]})'.replace(' ',
                                                                                                              '%20'),
        axis=1).values.tolist()

    def parse(self, response):
        title_year = response.url.split('search=')[-1].replace('%20', ' ')
        top_results = response.xpath('//search-page-media-row')
        for result in top_results:
            year = result.xpath('./@releaseyear').extract_first()
            title = result.xpath('.//a[@slot="title"]//text()').extract_first().strip()
            url = result.xpath('.//a[@slot="title"]//@href').extract_first()

            year_search = re.search(r'\d{4}', title_year).group()
            if str(year_search) == str(year) and title_year.replace(f' ({year_search})', '').replace('&amp;',
                                                                                                     '&') == title:
                yield scrapy.Request(url, callback=self.parse_movie)
                break

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
        item['theater_release_date'] = item_attributes[
            'Release Date (Theaters)'] if 'Release Date (Theaters)' in item_attributes else None
        item['DVD_release_date'] = item_attributes[
            'Release Date (Streaming)'] if 'Release Date (Streaming)' in item_attributes else None
        item['list_of_genres'] = item_attributes['Genre'] if 'Genre' in item_attributes else None
        item['abridged_list_of_cast'] = ', '.join([item.replace('\n', ' ').strip() for item in response.xpath(
            '//div[@class="cast-item media inlineBlock  "]//a//span//text()').extract()])
        item['abridged_list_of_directors'] = item_attributes['Director'] if 'Director' in item_attributes else None
        return item
