#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description: 插件控制器,用于在群聊天中开关插件和查看说明
@Date     :2021/10/19 13:29:10
@Author      :yuejieyao
@version      :1.0
'''
from re import L
from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.http.miraiMessageRequest import MiraiMessageRequest as MMR
from modules.message.messageType import Plain
from ..miraiPlugin import MiraiMessagePluginProcessor
from modules.message.messageChain import MessageChain
from modules.utils import log as Log
from prettytable import PrettyTable
import traceback
import re


@MiraiMessagePluginProcessor.mirai_group_message_plugin_register('Control')
class Control:
    NAME = "插件控制器"
    DESCRIPTION = """查看群插件清单: /功能
    打开插件 /打开(open) 插件注册名
    关闭插件 /关闭(close) 插件注册名 
    """

    def process(self, chains: MessageChain, group: int, target: int, quote: int):
        msg_display = chains.asDisplay().strip()
        if msg_display == '/功能':
            try:
                ds = MiraiDataSource()
                plugins = ds.getGroupPlugins(group=group)

                x = PrettyTable()
                # x.align = "l"
                x.field_names = ['注册名称', '功能', '是否打开']
                x.add_rows(plugins)

                MMR().sendGroupMessage(msg=MessageChain([Plain('输入:/查看 注册名称 即可查看对应插件说明\n'),
                                                         Plain(text='输入:/打开或关闭 注册名称即可切换插件状态\n'),
                                                         Plain(text=x.get_string(vertical_char='l'))]), target=group)
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
        elif re.match('/打开 .*', msg_display) != None or re.match('/open .*', msg_display) != None:
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
        elif re.match('/关闭 .*', msg_display) != None or re.match('/close .*', msg_display) != None:
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
        elif re.match('/查看 .*', msg_display) != None or re.match('/show .*', msg_display) != None:
            try:
                ds = MiraiDataSource()
                msgs = msg_display.split(' ')
                if ds.existGroupPlugin(register_name=msgs[1]):
                    MMR().sendGroupMessage(msg=MessageChain(
                        [Plain(text=ds.getDescription(register_name=msgs[1]))]), target=group)
                    Log.info(f'[Control][(Group){group}] show plugin description {msgs[1]}')
            except Exception as e:
                Log.error(msg=traceback.format_exc())
                MMR().sendGroupMessage(msg=MessageChain([Plain(text=str(e))]), target=group)
