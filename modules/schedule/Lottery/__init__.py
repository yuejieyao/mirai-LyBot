#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 定时任务,每日上午10点彩票开奖功能
@Date     :2021/11/18 10:59:18
@Author      :yuejieyao
@version      :1.0
'''

from typing import List
from ..miraiSchedule import MiraiScheduleProcessor
from modules.dataSource.userDataSource import DataSource
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, At
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.utils import log as Log
import traceback
import random


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(hour=10, minute=0)
class Pixiv:
    user_db = 'modules/resource/data/user.db'

    def process(self):
        try:
            # 生成今日的开奖号码
            first_prize = [random.randint(1, 16), random.randint(1, 16), random.randint(1, 16), random.randint(
                1, 16), random.randint(1, 16), random.randint(1, 16), random.randint(1, 8)]
            Log.info(msg=f"[Schedule][Lottery]今日大奖: {first_prize}", log=True)
            ds = DataSource(self.user_db)
            groups = ds.get_lottery_yesterday_group()
            if len(groups):
                for group in groups:
                    msg = MessageChain([Plain(text=f'今日大奖: {",".join(map(str,first_prize))}\n')])
                    qqs = ds.get_lottery_yesterday_qq(group=group)
                    if len(qqs):
                        for qq in qqs:
                            msg.extend([At(target=qq), Plain(text=' 您的彩票如下:\n')])
                            r = ds.get_lottery_yesterday_group_qq(group=group, qq=qq)
                            for i in r:
                                lvl, lvr = self.checkLettory(first_prize=first_prize,
                                                             lettory=list(map(i[0].split(','))))
                                """
                                奖励规则: 在第7位不等时,前6位中2至6位相等,对应7,6,5,4,3等奖
                                         在第7位相等时,前6位中0至6位相等,对应7,6,5,4,3,2,1等奖
                                """
                                money = 0
                                if lvr == 0:
                                    if lvl < 2:
                                        msg.append(Plain(text=f"{i[0]} 非的一批\n"))
                                    else:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得{9-lvl}等奖,奖励{500*(lvl-1)}游戏币\n"))
                                        money = 500*(lvl-1)

                                else:
                                    if lvl == 6:
                                        msg.append(Plain(text=f"{i[0]} 您可牛逼大了,头奖!奖励3000000游戏币,您永远都用不完\n"))
                                        money = 3000000
                                    elif lvl == 5:
                                        msg.append(Plain(text=f"{i[0]} 您可牛逼大了,二等奖!奖励300000游戏币,离头奖只差1位,真的可惜\n"))
                                        money = 300000
                                    else:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得{7-lvl}等奖,奖励{500*(lvl+1)}游戏币\n"))
                                        money = 500*(lvl+1)
                                if money:
                                    ds.add_money(qq=qq, money=money)
                    MMR().sendGroupMessage(msg=msg, target=group)

        except:
            Log.error(msg=traceback.format_exc())

    def checkLettory(self, first_prize: List, lettory: List) -> int:
        lv_left, lv_right = 0, 0
        if first_prize[6] == lettory[6]:
            lv_right = 1
        for i in range(6):
            if first_prize[i] == lettory[i]:
                lv_left = lv_left+1
        return lv_left, lv_right
