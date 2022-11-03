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
import random
from datetime import datetime, timedelta

from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Plain, Image, At
from modules.plugins.Genshin.modules.utils import messageUtils
from modules.plugins.Genshin.modules.utils.dataSource import DataSource
from modules.plugins.Genshin.modules.utils.genshinUtils import GenshinUtils
from modules.utils import log
from ..miraiSchedule import MiraiScheduleProcessor


def retrySign(award_info, cookie, group, qq, count):
    msg_req = MiraiMessageRequest()
    try:
        msg_req.sendGroupMessage(MessageChain([Plain(f"正在尝试重新签到,group={group},qq={qq}")]), target=group)
        nick_name = MiraiMemberRequests().getGroupMemberInfo(group=group, qq=qq).nickname
        content = f"{nick_name}({qq}):  "
        utils = GenshinUtils(cookie=cookie)
        role = utils.getRole()
        if not role:
            raise Exception("获取角色失败,请重新绑定")
        sign_info = utils.getSignInfo(role=role)
        if not sign_info:
            raise Exception("获取签到信息失败,请重新绑定")
        if sign_info['is_sign']:
            raise Exception("已经签到过了")
        if sign_info['first_bind']:
            raise Exception("需要在米游社手动签到一次")
        if utils.sign(role=role):
            content += f"尝试重新签到成功({count}/3)\n"
            path = messageUtils.create_sign_pic(award_info=award_info, content=content)
            msg_req.sendGroupMessage(MessageChain([Image(image_type='group', file_path=path)]), target=group)
        else:
            if count < 3:
                kwargs = {
                    "award_info": award_info,
                    "cookie": cookie,
                    "group": group,
                    "qq": qq,
                    "count": count + 1
                }
                m = random.randint(5, 15)
                MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                    run_date=datetime.now() + timedelta(minutes=m), func=retrySign, **kwargs)
                msg_req.sendGroupMessage(
                    MessageChain([Plain(f"尝试重新签到失败,将在{m}分后再次执行({count}/3),group={group},qq={qq}")]),
                    target=group)
            else:
                msg_req.sendGroupMessage(MessageChain([Plain(f"尝试重新签到失败({count}/3),group={group},qq={qq}")]),
                                         target=group)
    except Exception as e:
        msg_req.sendGroupMessage(MessageChain([Plain(f"尝试重新签到失败,group={group},qq={qq}\n"),
                                               Plain(str(e))]), target=group)


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
                    res = GenshinUtils(cookie=bind[1], ua=bind[2]).getAwardInfo()
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
                    nick_name = member_req.getGroupMemberInfo(group=group.id, qq=bind[0]).nickname
                    content += f"{nick_name}({bind[0]}):  "
                    utils = GenshinUtils(cookie=bind[1], ua=bind[2])
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
                        m = random.randint(5, 15)
                        content += f"签到失败,将在{m}分后重试\n"
                        kwargs = {
                            "award_info": award_info,
                            "cookie": bind[1],
                            "group": group.id,
                            "qq": bind[0],
                            "count": 1
                        }
                        MiraiScheduleProcessor().mirai_schedule_plugin_timing_register(
                            run_date=datetime.now() + timedelta(minutes=m), func=retrySign, **kwargs)

                path = messageUtils.create_sign_pic(award_info=award_info, content=content)
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Image(image_type='group', file_path=path)]),
                                                       target=group.id)

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
