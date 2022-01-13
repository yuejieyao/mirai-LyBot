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
from modules.dataSource.miraiDataSource import MiraiDataSource as MD
from datetime import datetime, timedelta
import requests


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('Newspaper', 8, 30)
class Newspaper:
    NAME = "每日60秒早报"
    DESCRIPTION = "每日早上8点半触发发送60秒早报"

    def process(self):
        msgReq = MiraiMessageRequest()
        try:
            msg = self.getNewsImg()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                if MD().isScheduleClose(register_name='Newspaper', group=group):
                    continue
                msgReq.sendGroupMessage(msg=msg, target=group.id)
        except Exception as e:
            msg = MessageChain([Plain(text="调用每日60秒早报失败,将在5分钟后重新调用")])
            msgReq.sendAdminMessage(msg=msg)

            MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                run_date=datetime.now()+timedelta(minutes=5), func=self.process)

    def getNewsImg(self) -> MessageChain:
        resp = requests.session().get('http://api.2xb.cn/zaob')
        resp.raise_for_status()
        result = resp.json()
        if 'imageUrl' in result:
            msg = MessageChain([Image(image_type="group", image_url=result['imageUrl'])])
            return msg
        else:
            raise Exception('Newspaper:获取数据失败')
