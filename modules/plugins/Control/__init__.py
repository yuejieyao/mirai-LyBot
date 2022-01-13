#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 插件控制器,用于在群聊天中开关插件和查看说明
@Date     :2021/10/19 13:29:10
@Author      :yuejieyao
@version      :1.0
'''
from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Plain, Image
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.utils import log as Log, common
from prettytable import PrettyTable
import traceback
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Control')
class Control:
    NAME = "功能控制器"
    DESCRIPTION = """查看清单: /插件,/plugin,/轮询,/schedule
        查看说明: /查看插件,/showP,/查看轮询,/showS
        打开功能: /打开插件,/openP,/打开轮询,/openS,
        关闭功能: /关闭插件,/closeP,/关闭轮询,/closeS
    """

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay().strip()
        if msg_display in ('/插件', '/plugin'):
            try:
                ds = MiraiDataSource()
                plugins = ds.getGroupPlugins(group=group)
                x = PrettyTable()
                # x.align = "l"
                x.field_names = ['注册名称', '功能', '是否打开']
                x.add_rows(plugins)
                MMR().sendGroupMessage(msg=MessageChain([Plain('输入:/查看插件 注册名称 即可查看对应插件说明\n'),
                                                         Plain(text='输入:/打开或关闭插件 注册名称即可切换插件状态\n'),
                                                         Image(image_type="group", file_path=common.text_to_img(x.get_string(vertical_char='l')))]), target=group)
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif msg_display in ('/轮询', '/schedule'):
            try:
                ds = MiraiDataSource()
                schedules = ds.getSchedule(group=group)
                x = PrettyTable()
                x.field_names = ['注册名称', '功能', '是否打开']
                x.add_rows(schedules)
                MMR().sendGroupMessage(msg=MessageChain([Plain('输入:/查看轮询 注册名称 即可查看对应轮询服务说明\n'),
                                                         Plain(text='输入:/打开或关闭轮询 注册名称即可切换轮询服务状态\n'),
                                                         Image(image_type="group", file_path=common.text_to_img(x.get_string(vertical_char='l')))]), target=group)
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/打开插件 .*', msg_display) != None or re.match('/openP .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                # 确认插件存在
                if ds.existGroupPlugin(register_name=msgs[1]):
                    ds.openGroupPlugin(register_name=msgs[1], group=group)
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f'成功打开插件{msgs[1]}')]), target=group)
                    Log.info(f'[Control][(Group){group}] open plugin {msgs[1]}')
                else:
                    raise Exception('不存在的插件')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/关闭插件 .*', msg_display) != None or re.match('/closeP .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                # 确认插件存在
                if ds.existGroupPlugin(register_name=msgs[1]):
                    if msgs[1] != 'Control':
                        ds.closeGroupPlugin(register_name=msgs[1], group=group)
                        MMR().sendGroupMessage(msg=MessageChain([Plain(text=f'成功关闭插件{msgs[1]}')]), target=group)
                        Log.info(f'[Control][(Group){group}] close plugin {msgs[1]}')
                    else:
                        MMR().sendGroupMessage(msg=MessageChain([Plain(text='你不能,也不应该关闭Control')]), target=group)
                else:
                    raise Exception('不存在的插件')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/查看插件 .*', msg_display) != None or re.match('/showP .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                if ds.existGroupPlugin(register_name=msgs[1]):
                    MMR().sendGroupMessage(msg=MessageChain(
                        [Plain(text=ds.getPluginDescription(register_name=msgs[1]))]), target=group)
                    Log.info(f'[Control][(Group){group}] show plugin description {msgs[1]}')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/打开轮询 .*', msg_display) != None or re.match('/openS .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                # 确认轮询服务存在
                if ds.existSchedule(register_name=msgs[1]):
                    ds.openGroupSchedule(register_name=msgs[1], group=group)
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f'成功打开轮询{msgs[1]}')]), target=group)
                    Log.info(f'[Control][(Group){group}] open plugin {msgs[1]}')
                else:
                    raise Exception('不存在的轮询')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/关闭轮询 .*', msg_display) != None or re.match('/closeS .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                # 确认插件存在
                if ds.existSchedule(register_name=msgs[1]):
                    ds.closeGroupSchedule(register_name=msgs[1], group=group)
                    MMR().sendGroupMessage(msg=MessageChain([Plain(text=f'成功关闭轮询{msgs[1]}')]), target=group)
                    Log.info(f'[Control][(Group){group}] close schedule {msgs[1]}')

                else:
                    raise Exception('不存在的轮询')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/查看轮询 .*', msg_display) != None or re.match('/showS .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                if ds.existSchedule(register_name=msgs[1]):
                    MMR().sendGroupMessage(msg=MessageChain(
                        [Plain(text=ds.getScheduleDescription(register_name=msgs[1]))]), target=group)
                    Log.info(f'[Control][(Group){group}] show schedule description {msgs[1]}')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
