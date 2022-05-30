#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 原神相关功能
@Date     :2022/01/19 09:07:55
@Author      :yuejieyao
@version      :1.0
"""
import random
import time
import traceback
from datetime import datetime

from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image, At
from modules.plugins.Genshin.modules.utils import messageUtils
from modules.plugins.Genshin.modules.utils.dataSource import DataSource
from modules.plugins.Genshin.modules.utils.genshinUtils import GenshinUtils
from modules.utils import log
from ..miraiSchedule import MiraiScheduleProcessor


@MiraiScheduleProcessor.mirai_schedule_plugin_everyday_register(schedule_name='GenshinSchedule', hour=6, minute=10)
class GenshinSchedule:
    NAME = "原神每日签到"
    DESCRIPTION = "每日签到"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self):
        try:
            ds = DataSource(path=self.genshin_db)
            member_req = MiraiMemberRequests()
            groups = member_req.getGroupList()
            for group in groups:
                binds = ds.getGroupBinds(group=group.id)
                # 先获取签到奖励信息
                awards = None
                for bind in binds:
                    res = GenshinUtils(cookie=bind[1]).getAwardInfo()
                    if res:
                        awards = res
                        break
                    time.sleep(1)
                if not awards:
                    continue
                day = datetime.now().day
                award_info = awards[day - 1]

                content = ''
                for bind in binds:
                    time.sleep(random.randint(2, 5))
                    log.info(f'[Schedule][Genshin] Checking user [{group.id}(Group)][{bind[0]}(QQ)] ')
                    content += f"{member_req.getGroupMemberInfo(group=group.id, qq=bind[0]).nickname}({bind[0]}):  "
                    utils = GenshinUtils(cookie=bind[1])
                    role = utils.getRole()
                    if not role:
                        content += "获取角色失败,请重新绑定\n"
                        continue
                    sign_info = utils.getSignInfo(role=role)
                    if not sign_info:
                        content += "获取签到信息失败,请重新绑定\n"
                        continue
                    if sign_info['is_sign']:
                        content += "旅行者,你已经签到过了 \n"
                        continue
                    if sign_info['first_bind']:
                        content += "旅行者,你需要在米游社手动签到一次\n"
                        continue
                    if utils.sign(role=role):
                        content += "签到成功\n"
                    else:
                        content += "签到失败\n"
                path = messageUtils.create_sign_pic(award_info=award_info, content=content)
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Image(image_type='group', file_path=path)]), target=group.id)

        except:
            log.error(traceback.format_exc())


@MiraiScheduleProcessor.mirai_schedule_plugin_every_hour_register(schedule_name='GenshinResinSchedule', interval=2)
class GenshinResinSchedule:
    NAME = "原神体力提醒"
    DESCRIPTION = "2小时检测一次,超过150提醒一次,溢出提醒一次"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self):
        try:
            ds = DataSource(self.genshin_db)
            member_req = MiraiMemberRequests()
            groups = member_req.getGroupList()
            for group in groups:
                binds = ds.getGroupBinds(group=group.id)
                for bind in binds:
                    time.sleep(random.randint(2, 6))
                    qq = bind[0]
                    cookie = bind[1]
                    if not ds.existsResinRemind(group.id, qq):
                        ds.addResinRemind(group.id, qq)
                    try:
                        if not ds.isCloseResinRemind(group.id, qq):
                            resin = int(GenshinUtils(cookie).getRecordDaily()['current_resin'])
                            log.info(f"[Schedule][Genshin][(Group){group.id}][(Uid){qq}] checking resin = {resin} ")
                            if 150 <= resin < 160:
                                if not ds.isSend(group.id, qq):
                                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                                        [At(qq), Plain(f" 旅行者,您的当前体力已经{resin}了,快要溢出了哦")]), target=group.id)
                            elif resin >= 160:
                                if not ds.isSend(group.id, qq):
                                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                                        [At(qq), Plain(" 旅行者,您的当前体力已经溢出啦,赶紧上游戏做两个树脂吧")]), target=group.id)
                                    ds.setSend(group.id, qq)
                            else:
                                ds.setNotSend(group.id, qq)

                    except:
                        log.error(traceback.format_exc())
                        continue

        except:
            log.error(traceback.format_exc())
