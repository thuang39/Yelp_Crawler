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
        self.csvwriter.writerow(['hotel_href','hotel_name','hotel_rating','price_range','num_review','review_content','token_list','text_counter','bigram_best','trigram_best'])

    def process_item(self, item, yelp):
        self.csvwriter.writerow([item['hotel_href'].encode('utf-8'),item['hotel_name'].encode('utf-8'),item['hotel_rating'].encode('utf-8'),item['price_range'].encode('utf-8'),item['num_review'].encode('utf-8'),item['review_content'].encode('utf-8'),item['token_list'],item['text_counter'],item['bigram_best'],item['trigram_best']])
        return item
