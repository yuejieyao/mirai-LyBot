#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 历史上的今天,定时任务
@Date     :2021/07/23 15:46:26
@Author      :yuejieyao
@version      :1.0
'''
from ..miraiSchedule import MiraiScheduleProcessor
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.http.miraiMemberRequest import MiraiMemberRequests
import requests


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(1, '07:30')
class Today:
    def process(self):
        msgReq = MiraiMessageRequest()
        try:
            msg = self.getToday()
            groups = MiraiMemberRequests().getGroupList()
            for group in groups:
                msgReq.sendGroupMessage(msg=msg, target=group.id)
        except:
            msg = MessageChain([Plain(text="调用历史上的今天失败,请检查")])
            msgReq.sendAdminMessage(msg=msg)

    def getToday(self) -> MessageChain:
        resp = requests.session().get('https://www.ipip5.com/today/api.php?type=json')
        resp.raise_for_status()
        result = resp.json()
        if 'today' in result and 'result' in result:
            msg = MessageChain(
                [Plain(text=f"早上好,今天是{result['today']},历史上的今天,发生过:\n")])
            for item in result['result']:
                if '提供数据' not in item['title']:
                    msg.append(
                        Plain(text=f"在{item['year']}年,{item['title']}\n"))
            return msg
        else:
            raise Exception('Today:获取数据失败')
