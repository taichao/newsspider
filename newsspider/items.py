# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,Join

class NewsspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class NewsItem(scrapy.Item):
    """
     新闻model
    """
    url = scrapy.Field()
    title = scrapy.Field()
    datetime = scrapy.Field()
    comment_id = scrapy.Field()
    channel = scrapy.Field()
    src = scrapy.Field()
    srcurl = scrapy.Field()

class NewsLoader(ItemLoader):
    default_output_processor = Join()

class CommentItem(scrapy.Item):
    id        = scrapy.Field()
    rootid    = scrapy.Field()
    targetid  = scrapy.Field()
    time      = scrapy.Field()
    content   = scrapy.Field()
    userid    = scrapy.Field()
    nick  = scrapy.Field()
    head  = scrapy.Field()
    region = scrapy.Field()

class ProxyLoader(ItemLoader):
    default_output_processor = Join()
class ProxyItem(scrapy.Item):
    ip    = scrapy.Field()
    port  = scrapy.Field()
    ptype = scrapy.Field()
    level = scrapy.Field()
