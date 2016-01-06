# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.exporters import JsonItemExporter
import os,logging,datetime,json
from items import NewsItem,CommentItem,ProxyItem
from scrapy.exceptions import DropItem
import mysql.connector
from mysql.connector.errors import IntegrityError


class BaseFilePipeline(object):
    def __init__(self,saved_path):
        self.files = {}
        self.saved_path = saved_path
        self.exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings.get('SAVED_PATH'))
        return pipeline


    def open_spider(self, spider):
        tp = self.gettype()['name']
        filename = '%s_%s.json' % (spider.name,tp)
        filename = os.path.join(self.saved_path,filename)

        file_ = open(filename,'w+b')
        self.files[spider] = file_
        self.exporter = JsonItemExporter(file_,ensure_ascii=False,encoding='utf-8')
        self.exporter.start_exporting()

    def gettype():
        pass

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file_ = self.files.pop(spider)
        file_.close()

class JsonExportNewsPipeline(BaseFilePipeline):
    """
    新闻导出
    """
    def gettype(self):
        return {'name':'news'}

    def process_item(self, item, spider):
        if isinstance(item,NewsItem):
            if 'title' not in item:
                logging.warn('item title is None:%s' % item['url'])
            else:
                self.exporter.export_item(item)
                raise DropItem()

        return item


class JsonExportCommentPipeline(BaseFilePipeline):
    """
    评论导出
    """
    def gettype(self):
        return {'name':'comment'}

    def process_item(self, item, spider):
        if isinstance(item,CommentItem):
            self.exporter.export_item(item)
            raise DropItem()
        return item

class MysqlExportPipeline(object):
    def __init__(self,host,port,username,password,db):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(
            crawler.settings.get('DB_HOST'),
            crawler.settings.get('DB_PORT'),
            crawler.settings.get('DB_USERNAME'),
            crawler.settings.get('DB_PASSWORD'),
            crawler.settings.get('DB_NAME'),
        )
        return pipeline

    def open_spider(self, spider):
        self.context = mysql.connector.connect(
            host = self.host,
            port = self.port,
            user = self.username,
            password = self.password,
            database = self.db,
            charset = 'utf8'
        )

    def close_spider(self, spider):
        self.context.close()

    def process_item(self, item, spider):
        if isinstance(item,ProxyItem):
            cursor = self.context.cursor()
            add_proxy = ("insert into http_proxy_info(ip,port,type,level,update_time) values"
                         "(%s,%s,%s,%s,%s)"
                         )
            data = (
                item['ip'],
                item['port'],
                item['ptype'],
                item['level'],
                datetime.date.today()
            )
            print(data)
            print(item['level'])
            try:
                cursor.execute(add_proxy,data)
                self.context.commit()
            except Exception as e:
                if not isinstance(e,IntegrityError):
                    logging.error(e)
            finally:
                cursor.close()
        return item
