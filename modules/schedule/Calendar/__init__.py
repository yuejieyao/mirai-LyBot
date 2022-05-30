#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 摸鱼人日历(https://api.vvhan.com/api/moyu?type=json)
@Date     :2022/04/20 10:54:20
@Author      :yuejieyao
@version      :1.0
"""
from datetime import datetime, timedelta

import requests

from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from ..miraiSchedule import MiraiScheduleProcessor


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register('Calendar', 8, 30)
class Calendar:
    NAME = "摸鱼人日历"
    DESCRIPTION = "每日早上8点半触发发送摸鱼人日历"

    def process(self):
        msg_req = MiraiMessageRequest()
        try:
            msg = get_news_img()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                if MiraiDataSource().isScheduleClose(register_name='Calendar', group=group.id):
                    continue
                msg_req.sendGroupMessage(msg=msg, target=group.id)
        except:
            msg = MessageChain([Plain(text="调用摸鱼人日历失败,将在5分钟后重新调用")])
            msg_req.sendAdminMessage(msg=msg)

            MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                run_date=datetime.now() + timedelta(minutes=5), func=self.process)


def get_news_img() -> MessageChain:
    resp = requests.session().get('https://api.j4u.ink/proxy/remote/moyu.json')
    resp.raise_for_status()
    result = resp.json()
    if 'code' in result and result['code'] == 200:
        msg = MessageChain([Image(image_type="group", image_url=result['data']['moyu_url'])])
        return msg
    else:
        raise Exception('Calendar:获取数据失败')
