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
        
        next_page_xpath = '//span[@class="pagination-label u-align-middle responsive-hidden-small pagination-links_anchor"]/text()'
        if response.xpath(next_page_xpath).extract():
            req_20 = Request(url=item['hotel_href'] + '?start=20',callback=self.parse_hotel_review_20)
            req_20.meta['item'] = item
            yield req_20
        else:
            item['review_content_20'] = ''
            item['token_list_20'] = []
            item['review_content_40'] = ''
            item['token_list_40'] = []
            item['review_content_60'] = ''
            item['token_list_60'] = []
            item['review_content_80'] = ''
            item['token_list_80'] = []
            item['text_counter'] = item['token_list']+item['token_list_20']+item['token_list_40']+item['token_list_80']+item['token_list_60']+item['token_list_80']
            item['text_counter'] = Counter(item['text_counter']).most_common(100)
            
            bigram_measures = nltk.collocations.BigramAssocMeasures()
            trigram_measures = nltk.collocations.TrigramAssocMeasures()
            review_all = item['review_content']+item['review_content_20']+item['review_content_40']+item['review_content_60']+item['review_content_80']
            review_all_token = tokenizer.tokenize(review_all.lower())
            review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
            bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
            bigram_finder.apply_freq_filter(4)
            trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
            trigram_finder.apply_freq_filter(3)
            item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            yield item

    def parse_hotel_review_20(self,response):
        item = response.meta['item']
        hxs = HtmlXPathSelector(response)
        review_contents_20 = hxs.select('//div[@class="review-content"]//p').extract()
        review_contents_20 = ''.join(review_contents_20)
        review_contents_20 = unicodedata.normalize('NFKD', review_contents_20).encode('ascii','ignore').replace('<p itemprop="description" lang="en">','').replace('<br>','').replace('</p>','')
        item['review_content_20'] = review_contents_20
        tokenizer = RegexpTokenizer(r'\w+')
        review_contents_20 = tokenizer.tokenize(review_contents_20.lower())
        token_lists_20 = [word for word in review_contents_20 if word not in stopwords.words('english') and (len(word)<=22 and len(word)>=3) and word not in filter_words and word_check.check(word)]
        item['token_list_20'] = token_lists_20
        
        next_page_xpath = '//span[@class="pagination-label u-align-middle responsive-hidden-small pagination-links_anchor"]/text()'
        if response.xpath(next_page_xpath).extract():
            req_40 = Request(url=item['hotel_href'] + '?start=40',callback=self.parse_hotel_review_40)
            req_40.meta['item'] = item
            yield req_40
        else:
            item['review_content_40'] = ''
            item['token_list_40'] = []
            item['review_content_60'] = ''
            item['token_list_60'] = []
            item['review_content_80'] = ''
            item['token_list_80'] = []
            item['text_counter'] = item['token_list']+item['token_list_20']+item['token_list_40']+item['token_list_80']+item['token_list_60']+item['token_list_80']
            item['text_counter'] = Counter(item['text_counter']).most_common(100)

            bigram_measures = nltk.collocations.BigramAssocMeasures()
            trigram_measures = nltk.collocations.TrigramAssocMeasures()
            review_all = item['review_content']+item['review_content_20']+item['review_content_40']+item['review_content_60']+item['review_content_80']
            review_all_token = tokenizer.tokenize(review_all.lower())
            review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
            bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
            bigram_finder.apply_freq_filter(4)
            trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
            trigram_finder.apply_freq_filter(3)
            item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            yield item

    def parse_hotel_review_40(self,response):
        item = response.meta['item']
        hxs = HtmlXPathSelector(response)
        review_contents_40 = hxs.select('//div[@class="review-content"]//p').extract()
        review_contents_40 = ''.join(review_contents_40)
        review_contents_40 = unicodedata.normalize('NFKD', review_contents_40).encode('ascii','ignore').replace('<p itemprop="description" lang="en">','').replace('<br>','').replace('</p>','')
        item['review_content_40'] = review_contents_40
        tokenizer = RegexpTokenizer(r'\w+')
        review_contents_40 = tokenizer.tokenize(review_contents_40.lower())
        token_lists_40 = [word for word in review_contents_40 if word not in stopwords.words('english') and (len(word)<=22 and len(word)>=3) and word not in filter_words and word_check.check(word)]
        item['token_list_40'] = token_lists_40
        
        next_page_xpath = '//span[@class="pagination-label u-align-middle responsive-hidden-small pagination-links_anchor"]/text()'
        if response.xpath(next_page_xpath).extract():
            req_60 = Request(url=item['hotel_href'] + '?start=60',callback=self.parse_hotel_review_60)
            req_60.meta['item'] = item
            yield req_60
        else:
            item['review_content_60'] = ''
            item['token_list_60'] = []
            item['review_content_80'] = ''
            item['token_list_80'] = []
            item['text_counter'] = item['token_list']+item['token_list_20']+item['token_list_40']+item['token_list_80']+item['token_list_60']+item['token_list_80']
            item['text_counter'] = Counter(item['text_counter']).most_common(100)

            bigram_measures = nltk.collocations.BigramAssocMeasures()
            trigram_measures = nltk.collocations.TrigramAssocMeasures()
            review_all = item['review_content']+item['review_content_20']+item['review_content_40']+item['review_content_60']+item['review_content_80']
            review_all_token = tokenizer.tokenize(review_all.lower())
            review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
            bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
            bigram_finder.apply_freq_filter(4)
            trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
            trigram_finder.apply_freq_filter(3)
            item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            yield item
    
    def parse_hotel_review_60(self,response):
        item = response.meta['item']
        hxs = HtmlXPathSelector(response)
        review_contents_60 = hxs.select('//div[@class="review-content"]//p').extract()
        review_contents_60 = ''.join(review_contents_60)
        review_contents_60 = unicodedata.normalize('NFKD', review_contents_60).encode('ascii','ignore').replace('<p itemprop="description" lang="en">','').replace('<br>','').replace('</p>','')
        item['review_content_60'] = review_contents_60
        tokenizer = RegexpTokenizer(r'\w+')
        review_contents_60 = tokenizer.tokenize(review_contents_60.lower())
        token_lists_60 = [word for word in review_contents_60 if word not in stopwords.words('english') and (len(word)<=22 and len(word)>=3) and word not in filter_words and word_check.check(word)]
        item['token_list_60'] = token_lists_60
        
        next_page_xpath = '//span[@class="pagination-label u-align-middle responsive-hidden-small pagination-links_anchor"]/text()'
        if response.xpath(next_page_xpath).extract():
            req_80 = Request(url=item['hotel_href'] + '?start=80',callback=self.parse_hotel_review_80)
            req_80.meta['item'] = item
            yield req_80
        else:
            item['review_content_80'] = ''
            item['token_list_80'] = []
            item['text_counter'] = item['token_list']+item['token_list_20']+item['token_list_40']+item['token_list_80']+item['token_list_60']+item['token_list_80']
            item['text_counter'] = Counter(item['text_counter']).most_common(100)

            bigram_measures = nltk.collocations.BigramAssocMeasures()
            trigram_measures = nltk.collocations.TrigramAssocMeasures()
            review_all = item['review_content']+item['review_content_20']+item['review_content_40']+item['review_content_60']+item['review_content_80']
            review_all_token = tokenizer.tokenize(review_all.lower())
            review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
            bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
            bigram_finder.apply_freq_filter(4)
            trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
            trigram_finder.apply_freq_filter(3)
            item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
            yield item

    def parse_hotel_review_80(self,response):
        item = response.meta['item']
        hxs = HtmlXPathSelector(response)
        review_contents_80 = hxs.select('//div[@class="review-content"]//p').extract()
        review_contents_80 = ''.join(review_contents_80)
        review_contents_80 = unicodedata.normalize('NFKD', review_contents_80).encode('ascii','ignore').replace('<p itemprop="description" lang="en">','').replace('<br>','').replace('</p>','')
        item['review_content_80'] = review_contents_80
        tokenizer = RegexpTokenizer(r'\w+')
        review_contents_80 = tokenizer.tokenize(review_contents_80.lower())
        token_lists_80 = [word for word in review_contents_80 if word not in stopwords.words('english') and (len(word)<=22 and len(word)>=3) and word not in filter_words and word_check.check(word)]
        item['token_list_80'] = token_lists_80
        item['text_counter'] = item['token_list']+item['token_list_20']+item['token_list_40']+item['token_list_80']+item['token_list_60']+item['token_list_80']
        item['text_counter'] = Counter(item['text_counter']).most_common(100)

        bigram_measures = nltk.collocations.BigramAssocMeasures()
        trigram_measures = nltk.collocations.TrigramAssocMeasures()
        review_all = item['review_content']+item['review_content_20']+item['review_content_40']+item['review_content_60']+item['review_content_80']
        review_all_token = tokenizer.tokenize(review_all.lower())
        review_all_filter = [word for word in review_all_token if word_check.check(word) and (len(word)<=22 and len(word)>=3) and word not in filter_words]
        bigram_finder = BigramCollocationFinder.from_words(review_all_filter)
        bigram_finder.apply_freq_filter(4)
        trigram_finder = TrigramCollocationFinder.from_words(review_all_filter)
        trigram_finder.apply_freq_filter(3)
        item['bigram_best'] = sorted(bigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
        item['trigram_best'] = sorted(trigram_finder.ngram_fd.items(), key=lambda t: (-t[1], t[0]))
        yield item
        

'''
        if 'review_content' not in item:
            item['review_content'] = review_contents
        else:
            item['review_content'] = item['review_content'] + '|||' + review_contents
    
        next_page_xpath = '//a[@class="page-option prev-next next"]/@href'
        if response.xpath(next_page_xpath).extract():
            next_page_url = response.xpath(next_page_xpath).extract()
            next_page_url = unicodedata.normalize('NFKD', ''.join(next_page_url)).encode('ascii','ignore')
            review_req = Request(url=next_page_url,meta={'item': item},callback=self.parse_hotel_info)
            review_req.meta['item'] = item
            yield review_req
        else:
            yield item
'''
