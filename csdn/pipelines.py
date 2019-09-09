# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import DuplicateKeyError

from csdn.helps import ding


class CsdnResourceMongoPipeline(object):
    collection_name = 'resources'

    def __init__(self, mongo_uri, mongo_db):
        self.item_count = 0
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def close_spider(self, spider):
        self.client.close()
        finish_time = datetime.datetime.now()
        ding('spider closed, count ' + str(self.item_count) + ', time ' + str(round((finish_time - self.start_time).seconds / 60, 2)) + 'min')

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        # https://api.mongodb.com/python/current/tutorial.html#indexing
        # 创建索引, 保证资源唯一
        self.db.resources.create_index([('id', ASCENDING)], unique=True)
        # 爬虫开始时间
        self.start_time = datetime.datetime.now()
        ding('spider opened')

    def process_item(self, item, spider):
        try:
            self.db[self.collection_name].insert_one(dict(item))
            self.item_count += 1
        # except DuplicateKeyError as e:
        #     ding(str(e) + ' ' + str(dict(item)))
        finally:
            return item
