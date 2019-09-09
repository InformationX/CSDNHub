# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities, Proxy
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from csdn.helps import ding, get_proxy
from selenium.common.exceptions import NoSuchElementException

from csdn.items import ResourceItem
import json
import datetime
from csdn.settings import SELENIUM_SERVER
from json.decoder import JSONDecodeError


class ResourceSpider(scrapy.Spider):
    name = 'Resource'
    allowed_domains = ['download.csdn.net']
    page_size = 50
    start_urls = ['https://download.csdn.net/index.php/source/ajax_get_more_code?pageno=1&pagesize=' + str(page_size)]

    cookies_file = 'cookies.json'
    csdn_url = 'https://www.csdn.net/'

    def get_resource_html_url(self, resource_uploader_username, resource_id):
        return 'https://download.csdn.net/download/' + resource_uploader_username + '/' + resource_id

    def get_next_page_url(self, url):
        # https://download.csdn.net/index.php/source/ajax_get_more_code?pageno=5&pagesize=10
        pageno_start_index = url.find('=') + 1
        pageno_end_index = url.find('&')
        pageno = int(url[pageno_start_index:pageno_end_index]) + 1
        return 'https://download.csdn.net/index.php/source/ajax_get_more_code?pageno=' + str(pageno) + '&pagesize=' + str(self.page_size)

    def get_resource_uploader_url(self, resource_uploader_username):
        return 'https://me.csdn.net/' + resource_uploader_username

    def parse(self, response):
        if response.status != 200:
            ding('request failed ' + response.url)
        else:
            try:
                resources = json.loads(response.body.decode('utf-8'))
                for resource_id in resources:
                    resource_item = ResourceItem()
                    resource_item['id'] = resource_id
                    resource = resources[resource_id]
                    resource_item['name'] = resource.get('title')
                    resource_uploader_username = resource.get('username')
                    resource_item['uploader'] = resource_uploader_username
                    resource_item['uploader_url'] = self.get_resource_uploader_url(resource_uploader_username)
                    resource_item['html_url'] = self.get_resource_html_url(resource_uploader_username, resource_id)
                    resource_item['score'] = resource.get('sourcescore')
                    resource_item['upload_time'] = str(datetime.datetime.fromtimestamp(int(resource.get('pubdate_int'))))
                    resource_item['description'] = resource.get('description')
                    resource_item['tag'] = resource.get('tag')
                    resource_item['size'] = resource.get('sourcesize')
                    resource_item['type'] = resource.get('filetype')

                    yield scrapy.Request(resource_item['html_url'], callback=self.parse_star,
                                         meta={'item': resource_item})
                if len(resources) == self.page_size:
                    yield scrapy.Request(self.get_next_page_url(response.url), callback=self.parse)
            except JSONDecodeError as e:
                ding(str(e) + ' ' + response.url)
                yield scrapy.Request(response.url, callback=self.parse)

    def parse_star(self, response):
        if response.status != 200:
            ding('request failed ' + response.url)
        else:
            resource_item = response.meta['item']
            stars = response.xpath("/html/body/div[@class='meeting_main']/div[@class='download_new clearfix']/div[@id='detail_down_l']/div[@id='download_top']/div[@class='download_top_wrap clearfix']/div[@class='download_top_t']/dl[@class='download_dl']/dd/h3/span[@class='starts']/i[@class='fa fa-star yellow']")
            resource_item['star'] = len(stars)
            yield resource_item

    def parse_download_url(self, response):
        if response.status != 200:
            ding('request failed ' + response.url)
        else:
            resource_item = response.meta['item']
            resource_html_url = response.url
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': get_proxy().get('http')
            })
            desired_capabilities = DesiredCapabilities.CHROME
            proxy.add_to_capabilities(desired_capabilities)
            driver = webdriver.Remote(command_executor=SELENIUM_SERVER,
                                      desired_capabilities=desired_capabilities)
            try:
                # 先请求，再添加cookies
                # selenium.common.exceptions.InvalidCookieDomainException: Message: Document is cookie-averse
                driver.get(self.csdn_url)
                # 从文件中获取到cookies
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.loads(f.read())
                for c in cookies:
                    driver.add_cookie(
                        {'name': c['name'], 'value': c['value'], 'path': c['path'], 'domain': c['domain'],
                         'secure': c['secure']})
                driver.get(resource_html_url)

                # Python Selenium Timeout Exception Catch
                # https://codeday.me/bug/20190208/630039.html
                # 可能会存在资源不存在的情况, 导致元素找不到: https://download.csdn.net/download/stephenxindell/10490994
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.LINK_TEXT, u"VIP下载"))
                )
                element.click()

                # 先获取到元素，再获取属性值
                download_url_el = driver.find_element_by_xpath("//div[@id='vipIgnoreP']//div["
                                                               "@class='resource_dl_btn']//a")
                download_url = download_url_el.get_attribute('href')
                resource_item['download_url'] = download_url

                # 获取资源评分
                try:
                    stars = driver.find_element_by_xpath("/html/body/div[@class='meeting_main']/div[@class='download_new clearfix']/div[@id='detail_down_l']/div[@id='download_top']/div[@class='download_top_wrap clearfix']/div[@class='download_top_t']/dl[@class='download_dl']/dd/h3/span[@class='starts']/i[@class='fa fa-star yellow']")
                    resource_item['star'] = len(stars)
                except NoSuchElementException:
                    resource_item['star'] = 0
                yield resource_item

            except Exception as e:
                ding(str(e) + ' ' + resource_html_url)
            finally:
                driver.close()
