# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import csv,sys
csv.field_size_limit(sys.maxsize)
class YelpCrawlerPipeline(object):
    def __init__(self):
    	self.input = raw_input("Enter City Again: ")
        self.input = self.input.title().replace(" ","_")+"_Hotel_Review"
        self.csvwriter = csv.writer(open('%s.csv'% (self.input), 'wb'))
        self.csvwriter.writerow(['hotel_href','hotel_name','hotel_rating','price_range','num_review','review_content','review_content_20','review_content_40','review_content_60','review_content_80','token_list','token_list_20','token_list_40','token_list_60','token_list_80','text_counter','bigram_best','trigram_best'])

    def process_item(self, item, yelp):
        self.csvwriter.writerow([item['hotel_href'].encode('utf-8'),item['hotel_name'].encode('utf-8'),item['hotel_rating'].encode('utf-8'),item['price_range'].encode('utf-8'),item['num_review'].encode('utf-8'),item['review_content'].encode('utf-8'),item['review_content_20'].encode('utf-8'),item['review_content_40'].encode('utf-8'),item['review_content_60'].encode('utf-8'),item['review_content_80'].encode('utf-8'),item['token_list'],item['token_list_20'],item['token_list_40'],item['token_list_60'],item['token_list_80'],item['text_counter'],item['bigram_best'],item['trigram_best']])
        return item
