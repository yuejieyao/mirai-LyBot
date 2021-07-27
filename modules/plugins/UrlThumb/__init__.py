#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 链接地址快览,调用的outline接口(此插件仅面向如win10应用商店版QQ,不会自动生产预览卡片,outline接口需跨海)
@Date     :2021/07/19 15:22:04
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image, App, Xml
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
import requests
import re
import os
from lxml import etree
from PIL import Image as IMG
from io import BytesIO
import time
import json


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('urlThumb')
class UrlThumb:
    def process(self, chains: MessageChain, group: int, quote: int):
        if chains.has(App):
            json_msg = json.loads(chains.get(App)[0].content)
            try:
                desc = json_msg['desc']
                if desc == '新闻':
                    url = json_msg['meta']['news']['jumpUrl']
                    MsgReq().sendGroupMessage(msg=outline(url), target=group)
                    return
            except KeyError:
                pass
            else:
                url = json_msg['meta']['detail_1']['qqdocurl']
                MsgReq().sendGroupMessage(msg=outline(url), target=group)
        if chains.has(Xml):
            xml_msg = etree.fromstring(chains.get(Xml)[0].xml.encode('utf-8'))
            try:
                url = xml_msg.xpath('/msg/@url')[0]
                MsgReq().sendGroupMessage(msg=outline(url), target=group)
            except IndexError:
                pass
            else:
                pass
        else:
            urls = re.findall(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', chains.asDisplay())
            if len(urls) > 0:
                for url in urls:
                    MsgReq().sendGroupMessage(msg=outline(url), target=group)
                    time.sleep(1)  # 防调用频率过快


def outline(url: str) -> MessageChain:
    api_url = f"https://api.outline.com/v3/parse_article?source_url=%s" % url
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
        "Referer": "https://outline.com/",
    }

    try:
        response = get(url=api_url, headers=headers)
        result = response.json()
        if 'data' in result:
            msg = MessageChain([Plain(text='[快览] %s\n' % url),
                                Plain(text='[title] %s\n' % result['data']['title'])])
            if 'description' in result['data']:
                msg.append(Plain(text='[description] %s\n' %
                                 result['data']['description']))
            if 'domain' in result['data']:
                domain = result['data']['domain']
                # icon缓存目录
                temp_path = os.path.join(
                    os.path.dirname(__file__), 'icon_cache')
                if not os.path.exists(temp_path):
                    os.mkdir(temp_path)
                # icon缓存文件名
                path = os.path.join(
                    temp_path, f"{domain.replace('.','_')}.png")
                print('cache:%s' % path)
                # 如果没有就创建,有就直接调取发送
                if not os.path.exists(path):
                    try:
                        resp = get(
                            url=f'https://www.google.com/s2/favicons?domain={domain}')
                        image = IMG.open(BytesIO(resp.content))
                        image.save(path)
                    except:
                        print('cache error:no favicon')
                if os.path.exists(path):
                    msg.extend([
                        Plain(text='[favicon]\n'),
                        Image(image_type='group', file_path=path)
                    ])
            return msg
        else:
            msg = MessageChain([Plain(text='outline未返回数据')])
            return msg
    except:
        msg = MessageChain([Plain(text='outline调用失败')])
        return msg


def get(url, headers=None) -> requests.Response:
    response = requests.session().get(url=url, headers=headers)
    if response.status_code == 200:
        return response
    else:
        print(response)
        raise
