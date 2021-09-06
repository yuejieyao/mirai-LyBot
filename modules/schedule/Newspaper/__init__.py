#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 每日60秒早报(http://api.2xb.cn/)
@Date     :2021/09/03 13:48:03
@Author      :yuejieyao
@version      :1.0
'''
from ..miraiSchedule import MiraiScheduleProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
import requests


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(1, '08:30')
class Newspaper:
    def process(self):
        msgReq = MiraiMessageRequest()
        try:
            msg = self.getNewsImg()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                msgReq.sendGroupMessage(msg=msg, target=group.id)
        except Exception as e:
            print(e)
            msg = MessageChain([Plain(text="调用每日60秒早报失败,请检查")])
            msgReq.sendAdminMessage(msg=msg)

    def getNewsImg(self) -> MessageChain:
        resp = requests.session().get('http://api.2xb.cn/zaob')
        resp.raise_for_status()
        result = resp.json()
        if 'imageUrl' in result:
            msg = MessageChain([Image(image_type="group", image_url=result['imageUrl'])])
            return msg
        else:
            raise Exception('Newspaper:获取数据失败')
