from os import path
from modules.message.messageChain import MessageChain
from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.utils import log as Log
from threading import Thread


class MiraiMessagePluginProcessor:

    group_message_plugins_names = []  # 群消息插件注册名
    group_message_plugins = {}  # 群插件

    friend_message_plugins_name = []  # 好友消息插件注册名
    friend_message_plugins = {}  # 好友插件

    def __init__(self) -> None:
        self.db = MiraiDataSource()
        self.__initPluginData()
        self.db.close()

    def group_msg_process(self, msg: MessageChain, group: int, target: int, quote: int, plugins=()):
        """ 循环调用群消息插件

        Param:
            msg (MessageChain):消息
            group (int): 群号
            target (int): 发送者qq
            quote (int): 引用消息的messageId
            plugins (list[str]): 可选,按插件注册名指定触发某些插件
        """
        if plugins == ():
            # plugins = self.group_message_plugins_names
            plugins = MiraiDataSource().getGroupOpenedPlugins(group=group)

            for plugin_name in plugins:
                Thread(
                    self.group_message_plugins[plugin_name]().process(msg, group, target, quote)).start()

    @classmethod
    def mirai_group_message_plugin_register(cls, plugin_name):
        """ 注册为群消息的响应模块
        Param:
            plugin_name (str): 注册模块名
        """
        def wrapper(plugin):
            cls.group_message_plugins.update({plugin_name: plugin})
            cls.group_message_plugins_names.append(plugin_name)
            return plugin
        return wrapper

    def friend_msg_process(self, msg: MessageChain, target: int, quote: int, plugins=()):
        """ 循环调用私聊消息插件
        Param
            msg (MessageChain): 消息
            target (int): 私聊对象QQ
            quote (int): 引用消息的messageId
            plugins (List[str]): 可选,按插件注册名指定触发某些插件
        """
        if plugins == ():
            plugins = self.friend_message_plugins_name

            for plugin_name in plugins:
                Thread(
                    self.friend_message_plugins[plugin_name]().process(msg, target, quote)).start()

    @classmethod
    def mirai_friend_message_plugin_register(cls, plugin_name):
        """  注册为好友消息的响应模块
        Param
            plugin_name (str): 注册模块名
        """
        def wrapper(plugin):
            cls.friend_message_plugins.update({plugin_name: plugin})
            cls.friend_message_plugins_name.append(plugin_name)
            return plugin
        return wrapper

    def __initPluginData(self):
        """初始化插件数据库,用于功能开关和说明等需求"""

        # 删除已经不存在的插件
        plugin_register_names = self.db.query('select register_name from plugin')
        for row in plugin_register_names:
            if row[0] not in self.group_message_plugins_names+self.friend_message_plugins_name:
                self.db.removePlugin(register_name=row[0])
                Log.info(msg=f'remove plugin success : register_name = {row[0]}')

        # 增加或更新插件
        Log.info(msg='checking plugins datasource...')
        for register_name in self.group_message_plugins_names:
            self.db.addPlugin(register_name=register_name,
                              name=self.group_message_plugins[register_name].NAME, description=self.group_message_plugins[register_name].DESCRIPTION)

        for register_name in self.friend_message_plugins_name:
            self.db.addPlugin(register_name=register_name, name=self.friend_message_plugins[register_name].NAME,
                              description=self.friend_message_plugins[register_name].DESCRIPTION, plugin_type='friend')

        Log.info(msg='check plugins datasource success')
