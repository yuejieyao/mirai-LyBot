#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 疫情查询
@Date     :2022/05/07 15:34:12
@Author      :yuejieyao
@version      :1.0
"""
import re

import requests

from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.utils import common
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('NCov')
class NCov:
    NAME = "疫情查询"
    DESCRIPTION = """发送内容:疫情 地区名称,如:疫情 上海"""

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        message_display = chains.asDisplay()
        if re.match('疫情 .*', message_display) is None:
            return
        message_split = message_display.split(' ')
        msg_req = MsgReq()
        if len(message_split) == 2:
            msg_req.sendGroupMessage(msg=getNCov(
                message_split[1]), target=group)


def getNCov(keyword: str = None) -> MessageChain:
    province_names_api_url = "https://lab.isaaclin.cn/nCoV/api/provinceName"
    response = requests.session().get(province_names_api_url)
    response.raise_for_status()
    province_names = list(response.json()['results'])
    if keyword in province_names:
        province_name = keyword
    else:
        for name in province_names:
            if keyword in name:
                province_name = name
                break

    if province_name:
        ncov_api_url = f"https://lab.isaaclin.cn/nCoV/api/area?province={province_name}&latest=1"
        response = requests.session().get(ncov_api_url)
        response.raise_for_status()
        result = response.json()
        if "success" in result:
            province_info = result['results'][0]
            text = f"  名称: {province_name}\n" + \
                   f"  现存确诊人数: {province_info['currentConfirmedCount']}  \n" + \
                   f"  累计确诊人数: {province_info['confirmedCount']}  \n" + \
                   f"  疑似感染人数: {province_info['suspectedCount']}  \n" + \
                   f"  治愈人数: {province_info['curedCount']}  \n" + \
                   f"  死亡人数: {province_info['deadCount']}  \n"
            return MessageChain([Image(image_type='group', file_path=common.text_to_img(text))])
        else:
            pass
    else:
        return MessageChain([Plain(text="未找到相关国家或地区的疫情信息")])
