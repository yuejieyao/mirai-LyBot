#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 搜图
@Date     :2022/05/25 14:57:21
@Author      :yuejieyao
@version      :1.0
"""
import traceback
from urllib import parse

import requests

from modules.conf import config
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
from modules.utils import log
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('SearchImg')
class SearchImg:
    NAME = "搜图"
    DESCRIPTION = """搜图后发送图片"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        if chains.asDisplay() == '搜图':
            def _filter(_msg: MessageChain, _target: int, _group: int):
                if _target == target and _group == group:
                    if _msg.has(Image):
                        return True
                    elif _msg.asDisplay() in ['取消', '算了', 'cancel']:
                        return True
                    return False

            def _callback(_msg: MessageChain, _target: int, _group: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                imgs = _msg.get(Image)
                if len(imgs) > 0:
                    url = imgs[0].chain['url']
                    result = search_by_image_url(url)
                    try:
                        if 'header' in result and 'status' in result['header'] and result['header']['status'] == 0:
                            result = result['results'][0]
                            if 'jp_name' in result['data']:
                                title = result['data']['jp_name']
                            else:
                                title = result['data']['source']
                            message_chain = MessageChain([Plain(text="检测到来源:\n"), Plain(text=title + '\n')])
                            similarity = result['header']['similarity']
                            message_chain.append(Plain(text=f"相似度达到{similarity}%哦\n"))
                            if 'thumbnail' in result['header']:
                                message_chain.append(Image(image_type='group', image_url=result['header']['thumbnail']))
                            if 'ext_urls' in result['data']:
                                ext_urls = '\n'.join(result['data']['ext_urls'])
                                message_chain.extend([Plain(text="来源链接:\n"), Plain(text=ext_urls)])
                            if 'part' in result['data'] and 'est_time' in result['data']:
                                part = result['data']['part']
                                est_time = result['data']['est_time']
                                message_chain.append(Plain(text=f'\n出处为第{part}集的 {est_time}'))

                            MiraiMessageRequest().sendGroupMessage(msg=message_chain, target=group)
                        else:
                            log.info('[SearchImg]' + result)
                    except:
                        log.error(traceback.format_exc())

            MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="来图,我看看")]), target=group,
                                                   quote=quote)
            MiraiMessageMonitorHandler().add(
                MiraiMessageMonitor(monitor_type='GroupMessage', target=target, call_filter=_filter,
                                    call_func=_callback))  # 添加一次性监听


def search_by_image_url(url: str):
    api_key = config.getConf(section='saucenao', option='apiKey')
    resp = requests.get(
        "https://saucenao.com/search.php?db=999&output_type=2&numres=1&api_key={}&url={}".format(
            api_key, parse.quote_plus(url)))
    resp.raise_for_status()
    _result = resp.json()
    return _result
