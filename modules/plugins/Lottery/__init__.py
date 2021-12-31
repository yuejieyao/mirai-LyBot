#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 彩票
@Date     :2021/11/17 10:26:41
@Author      :yuejieyao
@version      :1.0
'''


from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import At, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.dataSource.userDataSource import DataSource
from modules.utils import log as Log
from typing import List
import random
import traceback


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Lottery')
class Lottery:
    NAME = "彩票"
    DESCRIPTION = """发送购买彩票,以500游戏币获得一张彩票"""
    user_db = 'modules/resource/data/user.db'

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        msg_display = chains.asDisplay()

        msg_split = msg_display.split(' ')

        if msg_split[0] in ['购买彩票', '买彩票', '获得彩票', '买票']:
            try:
                ds = DataSource(path=self.user_db)
                purchased_count = ds.count_lottery_today(qq=target)
                has_money = ds.get_money(qq=target)
                if purchased_count >= 3:
                    MMR().sendGroupMessage(MessageChain([Plain('您已到达购买上限,请明天再买吧')]), target=group, quote=quote)
                    return
                if has_money < 500:
                    MMR().sendGroupMessage(MessageChain([Plain('您已经连一张都买不起了')]), target=group, quote=quote)
                    return
                buy_count = 1
                buy_money = 500
                msg = MessageChain([Plain('')])
                if len(msg_split) > 1:
                    if msg_split[1].isdigit():
                        buy_count = int(msg_split[1])
                        buy_money = 500*buy_count
                        buy_flag = False
                        # 判断钱是否足够买这么多张,自动减少购买数量
                        if buy_count*500 > has_money:
                            buy_count = has_money//500
                            buy_money = 500*buy_count
                            buy_flag = True
                        # 判断购买后是否超出上限,自动减少购买数量
                        if purchased_count+buy_count > 3:
                            buy_count = 3-purchased_count
                            buy_money = 500*buy_count
                            buy_flag = True
                        if buy_flag:
                            msg.append(Plain(f'由于上限或金额问题,您只能买到{buy_count}张哦~\n'))
                for i in range(buy_count):
                    content = ds.buy(qq=target, group=group)
                    msg.append(Plain(f'您购买的号码为: {content}\n'))
                if ds.min_money(qq=target, money=buy_money):
                    msg.append(Plain(f'开奖时间为明日10点,您剩余的游戏币为{has_money-buy_money}'))
                MMR().sendGroupMessage(msg=msg, target=group, quote=quote)

            except:
                Log.error(msg=traceback.format_exc())
        elif msg_display in ['我的彩票', '看看彩票', '我的票', '看票', '看看票']:
            try:
                ds = DataSource(self.user_db)
                r = ds.get_lottery_today(qq=target)
                print(r)
                if len(r):
                    mc = MessageChain([Plain(text="您当前拥有以下号码:\n")])
                    for i in r:
                        print(i)
                        mc.append(Plain(text=f"{i[0]}\n"))
                    mc.append(Plain(text="开奖时间为明日上午10点,尽请期待"))
                    MMR().sendGroupMessage(msg=mc, target=group, quote=quote)
                else:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="您当前没有正在生效的彩券")]), target=group, quote=quote)
            except:
                Log.error(msg=traceback.format_exc())
        elif msg_display == '彩票规则':
            MMR().sendGroupMessage(msg=MessageChain([Plain(text="彩票由7个数字组成,其中前6位从1-27里随机抽取,最后一位从1-9里抽取\n"),
                                                     Plain(text="奖励规则:\n"),
                                                     Plain(text="六等奖:选6+1中2+1或中1+1或中0+1\n"),
                                                     Plain(text="五等奖:选6+1中4+0或中3+1\n"),
                                                     Plain(text="四等奖:选6+1中5+0或中4+1\n"),
                                                     Plain(text="三等奖:选6+1中5+1\n"),
                                                     Plain(text="二等奖:选6+1中6+0\n"),
                                                     Plain(text="一等奖:选6+1中6+1")]), target=group)
