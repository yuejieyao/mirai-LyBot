
from modules.conf import config
from lxml import etree
from datetime import datetime
import requests
import re


class RssUtils:
    def __init__(self):
        self.token = config.getConf(section='rsshub', option='AccessKey')

    def getChannel(self, url: str):
        resp = requests.session().get(url=f"{url}?key={self.token}")
        resp.raise_for_status()
        xml = etree.fromstring(resp.content)
        title = xml.xpath('/rss/channel/title')[0].text
        return title

    def getLatestRss(self, url: str):
        """return (guid, title, description, img, link, date)"""
        resp = requests.session().get(url=f"{url}?key={self.token}")
        resp.raise_for_status()
        xml = etree.fromstring(resp.content)
        item = xml.xpath('/rss/channel/item')[0]

        title = item.xpath('title')[0].text.splitlines()[0]

        description = item.xpath('description')[0].text
        # 提取description中的图片
        img = ','.join(re.findall('img src="(.*?)"', description, re.S))
        # 去除description中的html标签
        description = re.sub('<br>', '\n', description)
        description = re.sub('<img.+?>', '', description)
        description = re.sub('<frame.+?frame>', '', description)

        guid = item.xpath('guid')[0].text
        link = item.xpath('link')[0].text

        return tuple((guid, title, description, img, link, datetime.now().strftime('%y-%m-%d')))
