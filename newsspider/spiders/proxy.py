# -*- coding: utf-8 -*-
import scrapy,logging
from scrapy.loader.processors import MapCompose
from newsspider.items import ProxyItem,ProxyLoader


class ProxySpider(scrapy.Spider):
    name = "proxy"
    allowed_domains = ["haodailiip.com"]
    start_urls = (
        'http://www.haodailiip.com/guonei/110000/1',
        'http://www.haodailiip.com/guonei/110000/2',
        'http://www.haodailiip.com/guonei/110000/3',
        'http://www.haodailiip.com/guonei/110000/4',
        'http://www.haodailiip.com/guonei/110000/5',
        'http://www.haodailiip.com/guonei/110000/6',
    )

    def parse(self, response):
        for sel in response.css('.proxy_table tr'):
            ld = ProxyLoader(ProxyItem(),sel)
            ld.add_css('ip','td:nth-child(1)::text',MapCompose(unicode.strip))
            ld.add_css('port','td:nth-child(2)::text',MapCompose(unicode.strip))
            ld.add_css('ptype','td:nth-child(4)::text',MapCompose(unicode.strip,unicode.lower))
            ld.add_css('level','td:nth-child(5)::text',MapCompose(unicode.strip))
            a  = ld.get_css('td:nth-child(7)::text',MapCompose(unicode.strip))
            if a and 'ms' in a[0]:
                if 'IP' in ld.get_output_value('ip').upper():
                    continue
                else:
                    yield ld.load_item()


