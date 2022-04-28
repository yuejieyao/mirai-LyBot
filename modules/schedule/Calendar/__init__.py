#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 摸鱼人日历(https://api.vvhan.com/api/moyu?type=json)
@Date     :2022/04/20 10:54:20
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


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('Calendar', 8, 30)
class Calendar:
    NAME = "摸鱼人日历"
    DESCRIPTION = "每日早上8点半触发发送摸鱼人日历"

    def process(self):
        msgReq = MiraiMessageRequest()
        try:
            msg = self.getNewsImg()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                if MD().isScheduleClose(register_name='Calendar', group=group.id):
                    continue
                msgReq.sendGroupMessage(msg=msg, target=group.id)
        except Exception as e:
            msg = MessageChain([Plain(text="调用摸鱼人日历失败,将在5分钟后重新调用")])
            msgReq.sendAdminMessage(msg=msg)

            MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                run_date=datetime.now()+timedelta(minutes=5), func=self.process)

    def getNewsImg(self) -> MessageChain:
        resp = requests.session().get('https://api.vvhan.com/api/moyu?type=json')
        resp.raise_for_status()
        result = resp.json()
        if 'success' in result and result['success']:
            msg = MessageChain([Image(image_type="group", image_url=result['url'])])
            return msg
        else:
            raise Exception('Calendar:获取数据失败')
