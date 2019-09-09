# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ResourceItem(scrapy.Item):
    id = scrapy.Field()
    # 资源名称
    name = scrapy.Field()
    # 资源的网页地址
    html_url = scrapy.Field()
    # 资源的下载地址
    # download_url = scrapy.Field()
    # 资源评分
    star = scrapy.Field()
    # 下载所需积分
    score = scrapy.Field()
    # 资源介绍
    description = scrapy.Field()
    # 资源大小
    size = scrapy.Field()
    # 上传时间
    upload_time = scrapy.Field()
    # 资源标签
    tag = scrapy.Field()
    # 上传者
    uploader = scrapy.Field()
    # 上传者的主页
    uploader_url = scrapy.Field()
    # 资源类型
    type = scrapy.Field()

