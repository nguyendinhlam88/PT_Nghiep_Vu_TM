import scrapy


class IMDBItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    created_date = scrapy.Field()
    title = scrapy.Field()
    rating = scrapy.Field()
    budget = scrapy.Field()
    plot_description = scrapy.Field()
    box_office_gross = scrapy.Field()
    opening_weekend_gross = scrapy.Field()
