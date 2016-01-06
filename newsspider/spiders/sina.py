# -*- coding: utf-8 -*-
import scrapy,re,datetime,json
from newsspider.items import NewsItem,NewsLoader,CommentItem
from scrapy.loader.processors import TakeFirst,MapCompose
import urlparse


class SinaSpider(scrapy.Spider):
    name = "sina"
    allowed_domains = ["sina.com.cn"]
    cmturl = 'http://comment5.news.sina.com.cn/page/info?format=json&group=0&compress=1&ie=utf-8&oe=utf-8'
    start_urls = (
        'http://news.sina.com.cn/',
    )

    def parse(self, response):
        #get_news
        for url in response.xpath('//a/@href').extract():
            r = re.search(r'/c/',url)
            if r:
                yield scrapy.Request(url,self.parse_news)

    def parse_news(self,response):
        ld = NewsLoader(NewsItem(),response)
        ld.add_value('url',response.url)
        ld.add_css('title','.page-header h1::text')
        ld.add_value('channel','sina')
        datetime = response.css('.time-source').xpath('text()').extract()
        ld.add_value('datetime',datetime,MapCompose(unicode.strip))
        comment_id = ld.get_xpath('//meta[@name="comment"]/@content',TakeFirst())
        if comment_id:
            cc = comment_id.split(':')
            if len(cc) == 2:
                channel,comment_id = cc
        if comment_id and channel:
            yield ld.load_item()
            page = 1
            page_size = 20
            cmurl = '&channel=%s&newsid=%s&page=%s&page_size=%s' % (channel,comment_id,page,page_size)
            yield scrapy.Request(self.cmturl + cmurl,self.parse_comment)

    def parse_comment(self,response):
        res = response.body_as_unicode()
        res = json.loads(res)
        res = res['result']
        status = res['status']
        cmntlist = res['cmntlist']
        if status['code'] != 0:
            self.logger.warn('parse_comment code is %s' + status['code'])
            return
        if cmntlist:
            for cmt in cmntlist:
                itm = CommentItem()
                itm['id'] = cmt['uid'] if 'uid' in cmt else None
                itm['rootid'] = cmt['mid'] if 'mid' in cmt else None
                itm['targetid'] = cmt['newsid'] if 'newsid' in cmt else None
                itm['time'] = cmt['time'] if 'time' in cmt else None
                itm['content'] = cmt['content'] if 'content' in cmt else None
                itm['nick'] =cmt['nick'] if 'nick' in cmt else None
                itm['region'] =cmt['area'] if 'area' in cmt else None
                yield itm
            ud = urlparse.urlparse(response.url)
            param = urlparse.parse_qs(ud.query)
            if 'page' in param:
                page = int(param['page'][0])
                page = page + 1
            else:
                self.warn('not page in query:%s' % response.url)
                page = 1
            q = (param['channel'][0],param['newsid'][0],str(page),param['page_size'][0])
            cmurl = '&channel=%s&newsid=%s&page=%s&page_size=%s' % q
            print(self.cmturl + cmurl)
            yield scrapy.Request(self.cmturl + cmurl,self.parse_comment)




