import json
import os

import requests

from csdn.helps import get_random_user_agent, get_proxy, ding


# cookies文件存放到项目根路径下
current_path = os.path.abspath(os.path.dirname(__file__))
root_path = current_path[0:current_path.rfind('csdn')]
cookies_file = root_path + 'cookies.json'


def download(resource_url, download_url):
    """
    下载资源

    :param download_url:
    :param resource_url: 资源地址
    :return:
    """

    resource_base_url = 'https://download.csdn.net'

    # ValueError: Invalid header name b':authority'
    # https://blog.csdn.net/qq_41884582/article/details/86691319
    headers = {
        'authority': 'download.csdn.net',
        'method': 'GET',
        'path': download_url.split(resource_base_url)[1],
        'scheme': 'https',
        'accept': 'text/html,application/xhtml+xml,application/xml;'
                  'q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': resource_url,
        'upgrade-insecure-requests': '1',
        'user-agent': get_random_user_agent()
    }

    cookie_jar = requests.cookies.RequestsCookieJar()
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies = json.loads(f.read())
    if len(cookies) > 0:
        # 设置cookies
        for c in cookies:
            cookie_jar.set(c['name'], c['value'], path=c['path'], domain=c['domain'], secure=c['secure'],
                           rest={'HttpOnly': c['httpOnly']})

    with requests.get(download_url, cookies=cookie_jar, headers=headers, stream=True, proxies=get_proxy()) as r:

        if r.status_code == 200:
            # 获取文件名
            # 文件名乱码: https://www.jianshu.com/p/b535a9434120
            header = r.headers.get('Content-Disposition', None)
            if header is None:
                print('今日下载数已用完')
            else:
                filename = str(header.split('"')[1].encode('ISO-8859-1'), encoding='utf-8')
                print('下载文件: ' + filename)
        else:
            print('download request failed: ' + r.content.decode('utf-8'))


def call_csdn_resource_api():
    r = requests.get('https://download.csdn.net/index.php/source/ajax_get_more_code?pageno=24&pagesize=10')
    if r.status_code == 200:
        print(r.content)
        # error: json.loads(r.content.decode('unicode_escape'))
        print(json.loads(r.content.decode('utf-8')))


if __name__ == '__main__':

    # download(resource_url='https://download.csdn.net/download/weixin_38744207/11701273', download_url='https://download.csdn.net/index.php/vip_download/download_client/11701273/WHJMrwNw1k%252FEfyQir6Ssz%252FqLMbJACgX32CjAlxaEe9wngB%252F39PSUvsREr2Gh5DGGR5wnWzw2aZ5r2JmwAPbXsCYJznWt6INIHvBzQ6y%252FqRr4W3tksOygWpzzKpMz452nQU%252F9R2v%252BQ7DofhwDCeHJsqFqRPoL7FhKirjl%252Bd2XxfVgJ7U9rPeZvrFvAzxaooMAKzbQCr3JAl5%252BDuvGcpWDcnrTw8xfxMirYIONqi9WrUY7cLjlxvuKHBUNguZ28MSymF10%252FrPYNoNw%253D1487582755342')
    call_csdn_resource_api()