import datetime
import json
import random

import requests
from .settings import DINGTALK_AT, DINGTALK_ACCESS_TOKEN


def ding(content, at_mobiles=None, is_at_all=False):
    if at_mobiles is None:
        at_mobiles = DINGTALK_AT
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'msgtype': 'text',
        'text': {
            'content': 'csdn-spider: ' + content + ' at ' + str(datetime.datetime.now())
        },
        'at': {
            'atMobiles': at_mobiles,
            'isAtAll': is_at_all
        }
    }
    url = 'https://oapi.dingtalk.com/robot/send?access_token=' + DINGTALK_ACCESS_TOKEN
    requests.post(url, data=json.dumps(data), headers=headers)


def get_random_user_agent():
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3891.0 Safari/537.36 Edg/78.0.268.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.42 Safari/537.36',
    ]
    return random.choice(user_agent_list)


# http://ip.jiangxianli.com/?page=1
def get_proxy():
    proxies = ['http://113.121.22.229:9999', 'http://124.205.155.150:9090', 'http://1.197.204.8:9999']
    proxy = {
        'http': random.choice(proxies)
    }
    return proxy
