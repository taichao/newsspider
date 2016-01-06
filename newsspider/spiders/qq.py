# -*- coding: utf-8 -*-
import scrapy,re,logging,json
from scrapy.loader import ItemLoader
from newsspider.items import NewsItem,NewsLoader,CommentItem
from urlparse import urlparse,urljoin

class QqSpider(scrapy.Spider):
    name = "qq"
    cmturl = 'http://coral.qq.com/article'
    allowed_domains = ["qq.com"]
    start_urls = (
        'http://news.qq.com/',
    )
    custom_settings = {
        'download_timeout':5
    }

    def parse(self, response):
        #get_news
        for url in response.xpath('//a/@href').extract():
            r = re.search(r'/a/',url)
            if r:
                yield scrapy.Request(url,self.parse_news)

        #get navs
        for url in response.css('#channelNavPart a[href]::attr(href)').extract():
            yield scrapy.Request(url,self.parse)


    def parse_news(self, response):
        ld = NewsLoader(item=NewsItem(),response=response)
        ld.add_value('url',response.url)
        ld.add_css('title','div.main .hd>h1::text')
        ld.add_css('srcurl','div.main .hd .tit-bar .ll .color-a-1 a[href]::attr(href)')
        ld.add_css('src','div.main .hd .tit-bar .ll .color-a-1 a[href]::text')
        ld.add_css('datetime','div.main .hd .tit-bar .article-time::text')
        ld.add_value('channel',u'qq')
        ld.add_value('comment_id',response.body_as_unicode(),re='cmt_id\s?=\s?([\d\w]+)')
        yield ld.load_item()
        cmturl = '/%s/comment?commentid=0&reqnum=10' % ld.get_output_value('comment_id')
        cmturl = self.cmturl + cmturl
        yield scrapy.Request(cmturl,self.parse_comment)

    def parse_comment(self, response):
        res = response.body_as_unicode()
        res = json.loads(res)
        if str(res[ 'errCode' ]) != '0':
            self.logger.warning('comment errCode is %s with url=%s' % (res[ 'errCode' ],response.url))
            return
        data = res[ 'data' ]
        commentList = data[ 'commentid' ]
        for cmt in commentList:
            itm = CommentItem()
            itm['id'] = cmt['id'] if 'id' in cmt else None
            itm['rootid'] = cmt['rootid'] if 'rootid' in cmt else None
            itm['targetid'] = cmt['targetid'] if 'targetid' in cmt else None
            itm['time'] = cmt['time'] if 'time' in cmt else None
            itm['content'] = cmt['content'] if 'content' in cmt else None
            if 'userinfo' in cmt:
                user = cmt['userinfo']
                itm['userid'] = user['userid'] if 'userid' in user else None
                itm['nick'] = user['nick'] if 'nick' in user else None
                itm['head'] = user['head'] if 'head' in user else None
                itm['region'] = user['region'] if 'region' in user else None
            yield itm

        if data['hasnext']:

            commentid = data['last']
            reqnum = 20
            cmturl = '/%s/comment?commentid=%s&reqnum=%s' % (data['targetid'],commentid,reqnum)
            cmturl = self.cmturl + cmturl
            self.logger.info('new commenturl : %s' % cmturl)
            yield scrapy.Request(cmturl,self.parse_comment)


