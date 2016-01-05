# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.exporters import JsonItemExporter
import os,logging
from items import NewsItem,CommentItem


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
        return item

