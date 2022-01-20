#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 原神相关功能,由于cookie的安全问题,只允许在私聊中绑定cookie
@Date     :2022/01/18 10:57:59
@Author      :yuejieyao
@version      :1.0
'''

from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Image, Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from .modules.utils.genshinUtils import GenshinUtils
from .modules.utils.dataSource import DataSource
from .modules.utils import messageUtils
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitor, MiraiMessageMonitorHandler
from modules.utils import log as Log, common
from datetime import datetime, timedelta
import traceback
import time


@MiraiMessagePluginProcessor.mirai_friend_message_plugin_register('GenshinCookieBind')
class GenshinCookieBind:
    NAME = "原神cookie绑定"
    DESCRIPTION = "绑定原神cookie"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, target: int, quote: int):
        if chains.asDisplay() in ['绑定原神cookie', 'add genshin cookie']:
            MMR().sendFriendMessage(msg=MessageChain(
                [Plain(text="请回复要绑定的群号和米游社cookie,用|分割,或者回复或回复取消/算了/cancel来取消当前操作")]), target=target)

            def filter(_msg: MessageChain, _target: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return True
                msgs = _msg.asDisplay().split('|')
                if len(msgs) == 2:
                    if msgs[0].isdigit():
                        return True
                    else:
                        MMR().sendFriendMessage(msg=MessageChain(
                            [Plain(text="输入错误,请回复要绑定的群号和米游社cookie,用|分割,或者回复或回复取消/算了/cancel来取消当前操作")]), target=_target)
                        return False
                else:
                    return False

            def callback(_msg: MessageChain, _target: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                try:
                    msgs = _msg.asDisplay().split('|')
                    group = int(msgs[0])
                    cookie = msgs[1]
                    msgReq = MMR()
                    msgReq.sendFriendMessage(msg=MessageChain([Plain(text="正在校验cookie,请稍后")]), target=_target)
                    time.sleep(1)
                    if GenshinUtils(cookie=cookie).getSignInfo():
                        ds = DataSource(self.genshin_db)
                        if ds.addBind(group=group, qq=_target, cookie=cookie):
                            msgReq.sendFriendMessage(msg=MessageChain([Plain(text="校验成功,已成功绑定cookie")]), target=_target)
                    else:
                        msgReq.sendFriendMessage(msg=MessageChain([Plain(text="校验失败")]), target=_target)
                except:
                    Log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(MiraiMessageMonitor(type='FriendMessage', target=target, filter=filter, call=callback))  # 添加一次性监听


@MiraiMessagePluginProcessor.mirai_temp_message_plugin_register('GenshinCookieBind')
class GenshinCookieBind_Temp:
    NAME = "原神cookie绑定"
    DESCRIPTION = "绑定原神cookie"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        if chains.asDisplay() in ['绑定原神cookie', 'add genshin cookie']:
            MMR().sendTempMessage(msg=MessageChain(
                [Plain(text="请回复要绑定的米游社cookie,或者回复取消/算了/cancel来取消当前操作")]), target_group=group, target_qq=target)

            def filter(_msg: MessageChain, _target: int, _group: int):
                return True

            def callback(_msg: MessageChain, _target: int, _group: int):
                if _msg.asDisplay() in ('取消', '算了', 'cancel'):
                    return
                try:
                    cookie = _msg.asDisplay()
                    msgReq = MMR()
                    msgReq.sendTempMessage(msg=MessageChain(
                        [Plain(text="正在校验cookie,请稍后")]), target_group=_group, target_qq=_target)
                    time.sleep(1)
                    if GenshinUtils(cookie=cookie).getSignInfo():
                        ds = DataSource(self.genshin_db)
                        if ds.addBind(group=_group, qq=_target, cookie=cookie):
                            msgReq.sendTempMessage(msg=MessageChain(
                                [Plain(text="校验成功,已成功绑定cookie")]), target_group=_group, target_qq=_target)
                    else:
                        msgReq.sendTempMessage(msg=MessageChain(
                            [Plain(text="校验失败")]), target_group=_group, target_qq=_target)
                except:
                    Log.error(msg=traceback.format_exc())

            MiraiMessageMonitorHandler().add(MiraiMessageMonitor(type='TempMessage', group=group,
                                                                 target=target, filter=filter, call=callback))  # 添加一次性监听


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Genshin')
class Genshin:
    NAME = "原神相关功能"
    DESCRIPTION = "原神相关功能"

    genshin_db = 'modules/resource/data/genshin.db'

    def process(self, chains: MessageChain, group: int, target: int,  quote: int):
        msg_display = chains.asDisplay()
        if msg_display in ['我的原神', 'my genshin', '原神信息', 'genshin info']:
            try:
                self.get_genshin_info(group, target, quote)
            except:
                Log.error(msg=traceback.format_exc())
        if msg_display in ['我的深渊', 'my abyss', '深渊信息', 'abyss info']:
            try:
                self.get_genshin_abyss(group, target, quote)
            except:
                Log.error(msg=traceback.format_exc())
        if msg_display in ['原神体力', 'resin', 'genshin resin', '树脂']:
            try:
                self.get_genshin_resin(group, target, quote)
            except:
                Log.error(msg=traceback.format_exc())

    def get_genshin_info(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie = ds.getCookie(group=group, qq=target)
        if cookie:
            utils = GenshinUtils(cookie=cookie)
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
                MMR().sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

        else:
            MMR().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group, quote=quote)

    def get_genshin_resin(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie = ds.getCookie(group=group, qq=target)
        if cookie:
            utils = GenshinUtils(cookie)
            daily = utils.getRecordDaily()
            if daily:
                current_resin = daily['current_resin']
                max_resin = daily['max_resin']
                resin_recovery_seconds = int(daily['resin_recovery_time'])
                h = resin_recovery_seconds//3600
                m = (resin_recovery_seconds-h*3600)//60
                delta = timedelta(hours=h, minutes=m)
                resin_recovery_time = datetime.now()+delta
                MMR().sendGroupMessage(msg=MessageChain(
                    [Plain(text=f"当前树脂: {current_resin}/{max_resin}\n"),
                        Plain(text=f"恢复需要{h}时{m}分,预计将在{resin_recovery_time.strftime('%Y-%m-%d %H:%M:%S')}全部恢复")]), target=group, quote=quote)
            else:
                MMR().sendGroupMessage(msg=MessageChain(
                    [Plain(text="查询失败,请检查是否已在米游社打开对应隐私权限")]), target=group, quote=quote)

        else:
            MMR().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group, quote=quote)

    def get_genshin_abyss(self, group: int, target: int, quote: int):
        ds = DataSource(path=self.genshin_db)
        cookie = ds.getCookie(group=group, qq=target)
        if cookie:
            utils = GenshinUtils(cookie=cookie)
            role = utils.getRole()
            if role:
                abyss = utils.getRecordAbyss(role=role)
                if not abyss:
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text="获取深渊信息失败")]), target=group, quote=quote)
                    return
                if not abyss['floors']:
                    MMR().sendGroupMessage(msg=MessageChain(
                        [Plain(text="旅行者你可太懒了,本期深渊一层都没打")]), target=group, quote=quote)
                    return

                path = messageUtils.create_abyss_pic(role=role, abyss=abyss)
                MMR().sendGroupMessage(msg=MessageChain(
                    [Image(image_type='group', file_path=path)]), target=group, quote=quote)

        else:
            MMR().sendGroupMessage(msg=MessageChain([Plain(text="您尚未绑定原神帐号")]), target=group, quote=quote)