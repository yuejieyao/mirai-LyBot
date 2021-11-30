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
            l = range(1, 28)
            c = random.sample(l, 6)
            first_prize_left = random.sample(l, 6)
            first_prize_right = random.randint(1, 9)

            Log.info(
                msg=f"[Schedule][Lottery]今日大奖: {','.join(map(str,first_prize_left))},{first_prize_right}", log=True)
            ds = DataSource(self.user_db)
            groups = ds.get_lottery_yesterday_group()
            if len(groups):
                for group in groups:
                    msg = MessageChain(
                        [Plain(text=f"今日大奖: {','.join(map(str,first_prize_left))},{first_prize_right}\n")])
                    qqs = ds.get_lottery_yesterday_qq(group=group)
                    if len(qqs):
                        for qq in qqs:
                            msg.extend([At(target=qq), Plain(text=' 您的彩票如下:\n')])
                            r = ds.get_lottery_yesterday_group_qq(group=group, qq=qq)
                            for i in r:
                                lvl, lvr = self.checkLettory(first_prize_left=first_prize_left, first_prize_right=first_prize_right,
                                                             lettory=list(map(int, i[0].split(','))))
                                """
                                奖励规则:
                                        六等奖:选6+1中2+1或中1+1或中0+1
                                        五等奖:选6+1中4+0或中3+1
                                        四等奖:选6+1中5+0或中4+1
                                        三等奖:选6+1中5+1
                                        二等奖:选6+1中6+0
                                        一等奖:选6+1中6+1
                                """
                                money = 0
                                if lvr == 0:
                                    if lvl < 4:
                                        msg.append(Plain(text=f"{i[0]} 非的一批\n"))
                                    elif lvl == 4:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得五等奖,奖励1000游戏币\n"))
                                        money = 1000
                                    elif lvl == 5:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得四等奖,奖励20000游戏币\n"))
                                        money = 20000
                                    elif lvl == 6:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得二等奖,奖励300000游戏币\n"))
                                        money = 3000000
                                else:
                                    if lvl < 3:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得六等奖,奖励500游戏币\n"))
                                        money = 500
                                    elif lvl == 3:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得五等奖,奖励1000游戏币\n"))
                                        money = 1000
                                    elif lvl == 4:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得四等奖,奖励20000游戏币\n"))
                                        money = 20000
                                    elif lvl == 5:
                                        msg.append(Plain(text=f"{i[0]} 恭喜您获得三等奖,奖励30000游戏币\n"))
                                        money = 30000
                                    elif lvl == 6:
                                        msg.append(Plain(text=f"{i[0]} 您可牛逼大了,一等奖!奖励3000000游戏币\n"))
                                        money = 3000000
                                if money:
                                    ds.add_money(qq=qq, money=money)
                    MMR().sendGroupMessage(msg=msg, target=group)

        except:
            Log.error(msg=traceback.format_exc())

    def checkLettory(self, first_prize_left: List[int], first_prize_right: int, lettory: List) -> int:
        lv_left, lv_right = 0, 0
        if lettory[6] == first_prize_right:
            lv_right = 1
        for i in range(6):
            if lettory[i] in first_prize_left:
                lv_left = lv_left+1
        return lv_left, lv_right
