from typing import List
from modules.message.messageChain import MessageChain
from threading import Thread


class MiraiMessagePluginProcessor:
    group_message_plugins_names = []  # 群消息插件注册名
    group_message_plugins = {}  # 群插件

    friend_message_plugins_name = []  # 好友消息插件注册名
    friend_message_plugins = {}  # 好友插件

    def group_msg_process(self, msg: MessageChain, group: int, quote: int, plugins=()):
        """ 循环调用群消息插件

        Param:
            msg (MessageChain):消息
            group (int): 群号
            quote (int): 引用消息的messageId
            plugins (list[str]): 可选,按插件注册名指定触发某些插件
        """
        if plugins == ():
            plugins = self.group_message_plugins_names

            for plugin_name in plugins:
                Thread(
                    self.group_message_plugins[plugin_name]().process(msg, group, quote)).start()

        # if plugins == ():
        #     for plugin_name in self.group_message_plugins_names:
        #         self.group_message_plugins[plugin_name]().process(
        #             msg, group, quote)
        # else:
        #     for plugin_name in plugins:
        #         self.group_message_plugins[plugin_name]().process(
        #             msg, group, quote)

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
