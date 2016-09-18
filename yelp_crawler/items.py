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
    review_content_20 = Field()
    token_list_20 = Field()
    review_content_40 = Field()
    token_list_40 = Field()
    review_content_60 = Field()
    token_list_60 = Field()
    review_content_80 = Field()
    token_list_80 = Field()
    text_counter = Field()
    bigram_best = Field()
    trigram_best = Field()

