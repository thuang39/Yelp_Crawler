# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class YelpCrawlerItem(scrapy.Item):
    hotel_href = Field()
    hotel_name = Field()
    hotel_rating = Field()
    price_range = Field()
    num_review = Field()
    review_content = Field()
    token_list = Field()
    text_counter = Field()
    bigram_best = Field()
    trigram_best = Field()

