#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 签到
@Date     :2021/09/02 14:15:08
@Author      :yuejieyao
@version      :1.0
'''

from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import At, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.dataSource import DataSource
import numpy as np


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Sign')
class Sign:
    NAME = "签到"
    DESCRIPTION = """签到功能,发送内容包含以下关键词即可触发:签到,早安,早上好,午安,中午好,下午好,晚安,晚上好"""

    sign_db = 'modules/resource/data/sign.db'
    sign_keyword = ['签到', '早安', '早上好', '午安', '中午好', '下午好', '晚安', '晚上好']

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        msg_display = chains.asDisplay()
        if any(keyword if keyword in msg_display else False for keyword in self.sign_keyword):
            ds = DataSource(path=self.sign_db)
            if not ds.isSign(target):
                sign_text = self.get_draw()
                msg = MessageChain([At(target=target), Plain(text=" 签到成功,"), Plain(text=sign_text)])
                MMR().sendGroupMessage(msg=msg, target=group)
                ds.sign(qq=target, sign_text=sign_text)
            else:
                MMR().sendGroupMessage(msg=MessageChain([Plain(text="今天已经签到过了哦")]), target=group)

    def get_draw(self):
        element_list = ['大吉', '吉', '中吉', '小吉', '末吉', '凶', '大凶']
        prob_list = [0.22, 0.07, 0.12, 0.25, 0.14, 0.11, 0.09]
        sample_size = 1000
        samples = np.random.choice(a=element_list, size=sample_size, p=prob_list)
        draw = samples[np.random.randint(0, 1000)]
        if draw == '大吉':
            return '今天的运势是...大吉! 哇,好厉害!'
        elif draw in ['吉', '中吉', '小吉']:
            return '今天的运势是...%s~,今天也是美好的一天哦~' % draw
        elif draw == '末吉':
            return '今天的运势是...末吉~,请不要灰心,末吉也是吉哦~,'
        elif draw == '凶':
            return '今天的运势是...凶...一定要小心哦,要不今天就在家里摸鱼吧~'
        elif draw == '大凶':
            return '今天的运势是...大凶?呜哇呜哇?'
        else:
            return ''
