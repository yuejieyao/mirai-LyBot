#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 在群内说:来张色图(可跟空格加一个关键词),未接18X并且一次只返回单张,如有需要请自行改造
@Date     :2021/06/11 15:14:56
@Author      :yuejieyao
@version      :1.0
'''

from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image
from modules.http.miraiMessageRequest import MiraiMessageRequest as MsgReq
from modules.conf import config
import re
import requests


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Lolicon')
class Lolicon:

    NAME = "色图(Lolicon)"
    DESCRIPTION = """发送内容:来张色图 关键词(可选)"""

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        message_display = chains.asDisplay()
        if re.match('来张色图.*', message_display) == None and re.match('来点色图.*', message_display) == None:
            return
        message_split = message_display.split(' ')
        msgReq = MsgReq()
        if len(message_split) == 1:
            msgReq.sendGroupMessage(msg=self.getLoli(), target=group)
        elif len(message_split) == 2:
            msgReq.sendGroupMessage(msg=self.getLoli(
                message_split[1]), target=group)

    def getLoli(self, keyword: str = None) -> MessageChain:
        conf = config.getLoliconConf()
        apiKey = conf['apiKey']

        __api_url = f"https://api.lolicon.app/setu?apikey={apiKey}&r18=0"
        if keyword:
            __api_url = __api_url+"&keyword="+keyword
        try:
            response = requests.session().get(__api_url)
            if response.status_code == 200:
                result = response.json()
                if result['code'] == 0:
                    loli_data = result['data']
                    msg = MessageChain([Plain(text="来了来了~\n")])
                    for setu in loli_data:
                        msg.extend([Plain(text="title: %s\n" % setu['title']),
                                    Plain(text="author: %s\n" %
                                          setu['author']),
                                    Plain(text="tags: %s\n" %
                                          ','.join(setu['tags'])),
                                    Image(image_url=setu['url'], image_type='group')])
                        return msg

                else:
                    return MessageChain([Plain(text='call lolicon api failed for result code != 0')])

            else:
                return MessageChain([Plain(text='call lolicon api failed for response status code != 200')])
        except Exception as e:
            return MessageChain([Plain(text='call lolicon api failed')])
