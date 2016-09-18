import sys
import requests
import scrapy
import math
import unicodedata
import nltk
import enchant
from scrapy.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from scrapy import log
from scrapy.selector import HtmlXPathSelector, Selector
from scrapy.contrib.loader import ItemLoader
from scrapy.http import Request
from yelp_crawler.items import YelpCrawlerItem
from yelp_crawler.pipelines import YelpCrawlerPipeline
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.collocations import *
from collections import Counter

class MySpider(CrawlSpider):
    filter_words = ['would','should','could','might','may','did','do','can','is','was','are','were','one','two','get','got','stay','stayed','the','this','these','those','they','have','been','want','even','had','that']#'room','rooms','hotel'
    global filter_words
    word_check = enchant.Dict("en_US")
    global word_check
    name = 'yelp'
    allowed_domains = ["www.yelp.com"]
    base_url = 'http://www.yelp.com'
    global base_url
    review_url = 'http://www.yelp.com/search?start={0}&sortby=review_count&cflt=hotels&find_loc='
    location_input = raw_input("Enter City: ")
    location = location_input.replace(" ","+")
    review_url = review_url+location
    start_urls = [review_url.format(start) for start in [0,10,20,30]]
        
    def parse(self,response):
        hxs = HtmlXPathSelector(response)
        hotel_hrefs = hxs.select('//span[@class="indexed-biz-name"]/a/@href').extract()
        for hotel_href in hotel_hrefs:
            item = YelpCrawlerItem()
            req = Request(url=base_url + hotel_href,callback=self.parse_hotel_info)
            req.meta['item'] = item
            yield req

    def parse_hotel_info(self,response):
        item = response.meta['item']
        item['hotel_href'] = response.url
        hxs = HtmlXPathSelector(response)
        hotel_names = hxs.select('//div[@class="biz-page-header-left"]/h1/text()').extract()
        #hotel_names = hxs.select('//div[@class="review-wrapper"]/p/strong/text()').extract()
        hotel_ratings = hxs.select('//div[@class="rating-very-large"]/meta/@content').extract()
        price_ranges = hxs.select('//span[@class="business-attribute price-range"]/text()').extract()
        num_reviews = hxs.select('//span[@class="review-count rating-qualifier"]/span/text()').extract()
        review_contents = hxs.select('//div[@class="review-content"]//p').extract()
        
        for hotel_name,hotel_rating,price_range,num_review,review_content in zip(hotel_names,hotel_ratings,price_ranges,num_reviews,review_contents):
            item['hotel_name'] = hotel_name
            item['hotel_rating'] = hotel_rating
            item['price_range'] = price_range
            item['num_review'] = num_review
            
        review_contents = ''.join(review_contents)
        review_contents = unicodedata.normalize('NFKD', review_contents).encode('ascii','ignore').replace('<p itemprop="description" lang="en">','').replace('<br>','').replace('</p>','')
        item['review_content'] = review_contents
        tokenizer = RegexpTokenizer(r'\w+')
        review_contents = tokenizer.tokenize(review_contents.lower())
        token_lists = [word for word in review_contents if word not in stopwords.words('english') and (len(word)<=22 and len(word)>=3) and word not in filter_words and word_check.check(word)]
        item['token_list'] = token_lists
        
        #next_page_xpath = '//span[@class="pagination-label u-align-middle responsive-hidden-small pagination-links_anchor"]/text()'
        #if response.xpath(next_page_xpath).extract():
        item['text_counter'] = Counter(item['text_counter']).most_common(20)
            
        bigram_measures = nltk.collocations.BigramAssocMeasures()
        trigram_measures = nltk.collocations.TrigramAssocMeasures()
        
        review_all = item['review_content']
        review_all_token = tokenizer.tokenize(review_all.lower())
        review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
        bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
        bigram_finder.apply_freq_filter(4)
        trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
        trigram_finder.apply_freq_filter(3)
        item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
        item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
        yield item
