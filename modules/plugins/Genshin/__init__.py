#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description: 原神相关功能,由于cookie的安全问题,只允许在私聊中绑定cookie
@Date     :2022/01/18 10:57:59
@Author      :yuejieyao
@version      :1.0
"""

import re
import time
import traceback
from datetime import datetime, timedelta

from modules.http.miraiMemberRequest import MiraiMemberRequests
from modules.http.miraiMessageRequest import MiraiMessageRequest
from modules.message.messageChain import MessageChain
from modules.message.messageType import Image, Plain
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
from modules.utils import log, common
from .modules.utils import messageUtils
from .modules.utils.dataSource import DataSource
from .modules.utils.genshinUtils import GenshinUtils
from ..miraiPlugin import MiraiMessagePluginProcessor


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('GenshinCookieBind')
class GenshinCookieBind:
    NAME = "原神cookie绑定"
    DESCRIPTION = "绑定原神cookie"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, target: int, quote: int):
        if chains.asDisplay() in ['绑定原神cookie', 'add genshin cookie']:
            MiraiMessageRequest().sendFriendMessage(msg=MessageChain(
                [Plain(text="请回复要绑定的群号和米游社cookie,用|分割,或者回复或回复取消/算了/cancel来取消当前操作")]), target=target)

            def _filter(_msg: MessageChain, _target: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return True
                msgs = _msg.asDisplay().split('|')
                if len(msgs) == 2:
                    if msgs[0].isdigit():
                        return True
                    else:
                        MiraiMessageRequest().sendFriendMessage(msg=MessageChain(
                            [Plain(text="输入错误,请回复要绑定的群号和米游社cookie,用|分割,或者回复或回复取消/算了/cancel来取消当前操作")]), target=_target)
                        return False
                else:
                    return False

            def _callback(_msg: MessageChain, _target: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                try:
                    msgs = _msg.asDisplay().split('|')
                    group = int(msgs[0])
                    cookie = msgs[1]
                    msg_req = MiraiMessageRequest()
                    msg_req.sendFriendMessage(msg=MessageChain([Plain(text="正在校验cookie,请稍后")]), target=_target)
                    time.sleep(1)
                    if GenshinUtils(cookie=cookie).getSignInfo():
                        ds = DataSource(self.genshin_db)
                        if ds.addBind(group=group, qq=_target, cookie=cookie):
                            msg_req.sendFriendMessage(msg=MessageChain([Plain(text="校验成功,已成功绑定cookie")]),
                                                      target=_target)
                    else:
                        msg_req.sendFriendMessage(msg=MessageChain([Plain(text="校验失败")]), target=_target)
                except:
                    log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(
                MiraiMessageMonitor(monitor_type='FriendMessage', target=target, call_filter=_filter,
                                    call_func=_callback))  # 添加一次性监听


@MiraiMessagePluginProcessor.mirai_temp_message_plugin_register('GenshinCookieBind')
class GenshinCookieBindTemp:
    NAME = "原神cookie绑定"
    DESCRIPTION = "绑定原神cookie"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        if chains.asDisplay() in ['绑定原神cookie', 'add genshin cookie']:
            MiraiMessageRequest().sendTempMessage(msg=MessageChain(
                [Plain(text="请回复要绑定的米游社cookie,或者回复取消/算了/cancel来取消当前操作")]), target_group=group, target_qq=target)

            def _filter(_msg: MessageChain, _target: int, _group: int):
                return True

            def _callback(_msg: MessageChain, _target: int, _group: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                try:
                    cookie = _msg.asDisplay()
                    msg_req = MiraiMessageRequest()
                    msg_req.sendTempMessage(msg=MessageChain(
                        [Plain(text="正在校验cookie,请稍后")]), target_group=_group, target_qq=_target)
                    time.sleep(1)
                    if GenshinUtils(cookie=cookie).getSignInfo():
                        ds = DataSource(self.genshin_db)
                        if ds.addBind(group=_group, qq=_target, cookie=cookie):
                            msg_req.sendTempMessage(msg=MessageChain(
                                [Plain(text="校验成功,已成功绑定cookie")]), target_group=_group, target_qq=_target)
                    else:
                        msg_req.sendTempMessage(msg=MessageChain(
                            [Plain(text="校验失败")]), target_group=_group, target_qq=_target)
                except:
                    log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(MiraiMessageMonitor(monitor_type='TempMessage', group=group,
                                                                 target=target, call_filter=_filter,
                                                                 call_func=_callback))  # 添加一次性监听


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Genshin')
class Genshin:
    NAME = "原神相关功能"
    DESCRIPTION = "原神相关功能"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay()
        p = "(深渊|abyss|我的深渊|深渊阵容|我的阵容)\\s*\\d*"
        if msg_display in ['我的原神', 'my genshin', '原神信息', 'genshin info']:
            try:
                self.get_genshin_info(group, target, quote)
            except:
                log.error(msg=traceback.format_exc())
        elif msg_display in ['我的深渊', 'my abyss', '深渊信息', 'abyss info']:
            try:
                self.get_genshin_abyss(group, target, quote)
            except:
                log.error(msg=traceback.format_exc())
        elif msg_display in ['原神体力', 'resin', 'genshin resin', '树脂']:
            try:
                self.get_genshin_resin(group, target, quote)
            except:
                log.error(msg=traceback.format_exc())
        elif msg_display in ['打开原神体力提醒', '打开体力提醒', '打开原神树脂提醒', '打开树脂提醒', 'open genshin resin remind',
                             'open resin remind']:
            try:
                ds = DataSource(path=self.genshin_db)
                if ds.isCloseResinRemind(group, target):
                    if ds.openResinRemind(group, target):
                        MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain('打开原神树脂提醒成功')]), target=group,
                                                               quote=quote)
                else:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain('旅行者,您的树脂提醒功能已经打开')]), target=group,
                                                           quote=quote)
            except:
                log.error(traceback.format_exc())
        elif msg_display in ['关闭原神体力提醒', '关闭体力提醒', '关闭原神树脂提醒', '关闭树脂提醒', 'close genshin resin remind',
                             'close resin remind']:
            try:
                ds = DataSource(path=self.genshin_db)
                if not ds.isCloseResinRemind(group, target):
                    if ds.closeResinRemind(group, target):
                        MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain('关闭原神树脂提醒成功')]), target=group,
                                                               quote=quote)
                else:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain('旅行者,您的树脂提醒功能已经关闭')]), target=group,
                                                           quote=quote)
            except:
                log.error(traceback.format_exc())
        elif re.match(p, msg_display):
            try:
                floor = int(list(filter(None, re.findall("\\d*", msg_display)))[0])
                self.get_genshin_abyss_floor(group, target, quote, floor)
            except:
                log.error(traceback.format_exc())
        elif msg_display == "原神签到":
            try:
                ds = DataSource(path=self.genshin_db)
                cookie, ua = ds.getCookieAndUa(group=group, qq=target)
                if cookie is None:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定cookie")]), target=group,
                                                           quote=quote)
                    return
                utils = GenshinUtils(cookie=cookie, ua=ua)
                awards = utils.getAwardInfo()
                if not awards:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="获取奖励信息失败")]), target=group)
                    return
                award_info = awards[datetime.now().day - 1]
                role = utils.getRole()
                if not role:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="获取角色失败,请重新绑定")]), target=group)
                    return
                sign_info = utils.getSignInfo(role=role)
                if not sign_info:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="获取签到信息失败,请重新绑定")]),
                                                           target=group)
                    return
                if sign_info['is_sign']:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="旅行者,你已经签到过了")]), target=group,
                                                           quote=quote)
                    return
                if sign_info['first_bind']:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                        [Plain(text="旅行者,你需要在米游社手动签到一次")]), target=group, quote=quote)
                    return
                if utils.sign(role=role):
                    content = f"{MiraiMemberRequests().getGroupMemberInfo(group=group, qq=target).nickname}({target}):  "
                    MiraiMessageRequest().sendGroupMessage(
                        msg=MessageChain([Image(image_type='group', file_path=messageUtils.create_sign_pic(
                            award_info=award_info, content=content + "签到成功"))]), target=group, quote=quote)
                else:
                    MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="签到失败")]), target=group,
                                                           quote=quote)

            except:
                log.error(traceback.format_exc())

    def get_genshin_info(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie, ua = ds.getCookieAndUa(group=group, qq=target)
        if cookie:
            utils = GenshinUtils(cookie=cookie, ua=ua)
            content = ""
            role = utils.getRole()
            if role:
                content += f"UID: {role['game_uid']}  昵称: {role['nickname']}  等级:{role['level']}\n"
                info = utils.getRecordInfo(role=role)
                if info:
                    stats = info['stats']
                    content += f"活跃天数: {stats['active_day_number']}  成就数: {stats['achievement_number']}\n"
                    content += f"角色数量: {stats['avatar_number']}  深渊进度: {stats['spiral_abyss']}\n"

                    content += f"风神瞳数量: {stats['anemoculus_number']}  岩神瞳数量: {stats['geoculus_number']}\n"
                    content += f"雷神瞳数量: {stats['electroculus_number']}\n"

                    content += f"普通宝箱数量: {stats['common_chest_number']}  精致宝箱数量: {stats['exquisite_chest_number']}\n"
                    content += f"珍贵宝箱数量: {stats['precious_chest_number']}  华丽宝箱数量: {stats['luxurious_chest_number']}\n"
                    content += f"奇馈宝箱数量: {stats['magic_chest_number']}\n"
                path = common.text_to_img(content)
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

        else:
            MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group,
                                                   quote=quote)

    def get_genshin_resin(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie, ua = ds.getCookieAndUa(group=group, qq=target)
        if cookie:
            utils = GenshinUtils(cookie, ua)
            daily = utils.getRecordDaily()
            if daily:
                current_resin = daily['current_resin']
                max_resin = daily['max_resin']
                resin_recovery_seconds = int(daily['resin_recovery_time'])
                h = resin_recovery_seconds // 3600
                m = (resin_recovery_seconds - h * 3600) // 60
                delta = timedelta(hours=h, minutes=m)
                resin_recovery_time = datetime.now() + delta
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                    [Plain(text=f"当前树脂: {current_resin}/{max_resin}\n"),
                     Plain(text=f"恢复需要{h}时{m}分,预计将在{resin_recovery_time.strftime('%Y-%m-%d %H:%M:%S')}全部恢复")]),
                    target=group, quote=quote)
            else:
                MiraiMessageRequest().sendGroupMessage(msg=MessageChain(
                    [Plain(text="查询失败,请检查是否已在米游社打开对应隐私权限")]), target=group, quote=quote)

        else:
            MiraiMessageRequest().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group,
                                                   quote=quote)

    def get_genshin_abyss(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie, ua = ds.getCookieAndUa(group=group, qq=target)
        mm_req = MiraiMessageRequest()
        if cookie:
            utils = GenshinUtils(cookie=cookie, ua=ua)
            role = utils.getRole()
            if role:
                abyss = utils.getRecordAbyss(role=role)
                if not abyss:
                    mm_req.sendGroupMessage(msg=MessageChain([Plain(text="获取深渊信息失败")]), target=group, quote=quote)
                    return
                if not abyss['floors']:
                    mm_req.sendGroupMessage(msg=MessageChain(
                        [Plain(text="旅行者你可太懒了,本期深渊一层都没打")]), target=group, quote=quote)
                    return

                mm_req.sendGroupMessage(msg=MessageChain([Plain(text="正在出图...请稍后")]), target=group)
                path = messageUtils.create_abyss_pic(role=role, abyss=abyss)
                mm_req.sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

        else:
            mm_req.sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group, quote=quote)

    def get_genshin_abyss_floor(self, group: int, target: int, quote: int, floor_index: int):
        ds = DataSource(path=self.genshin_db)
        cookie, ua = ds.getCookieAndUa(group, target)
        mm_req = MiraiMessageRequest()
        if floor_index not in [9, 10, 11, 12]:
            mm_req.sendGroupMessage(msg=MessageChain([Plain(text="仅支持查询9-12层的深渊阵容信息")]), target=group)
        if cookie:
            utils = GenshinUtils(cookie=cookie, ua=ua)
            role = utils.getRole()
            if role:
                abyss = utils.getRecordAbyss(role=role)
                if not abyss:
                    mm_req.sendGroupMessage(msg=MessageChain([Plain(text="获取深渊信息失败")]), target=group, quote=quote)
                    return
                if not abyss['floors']:
                    mm_req.sendGroupMessage(msg=MessageChain(
                        [Plain(text="旅行者你可太懒了,本期深渊一层都没打")]), target=group, quote=quote)
                    return
                mm_req.sendGroupMessage(msg=MessageChain([Plain(text="正在出图...请稍后")]), target=group)
                path = messageUtils.create_abyss_floor_pic(role=role, abyss=abyss, index=floor_index)
                mm_req.sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

        else:
            mm_req.sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group, quote=quote)
