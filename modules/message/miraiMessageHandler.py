from modules.message.messageChain import MessageChain
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitorHandler
from modules.plugins.miraiPlugin import MiraiMessagePluginProcessor
from modules.conf import config
from modules.utils import log as Log


class MiraiMessageHandler:
    def __init__(self) -> None:
        self.processor = MiraiMessagePluginProcessor()
        self.monitors = MiraiMessageMonitorHandler()
        self.banList = config.getMiraiConf('banList').split(',')

    def onMessage(self, obj):
        """ 根据websocket传来的mirai message触发各种事件 """

        if 'type' not in obj:
            # 未知消息
            return False

        if obj['type'] == 'GroupMessage':
            # 群消息
            sender = obj["sender"]["id"]
            if str(sender) in self.banList:
                # banlist过滤
                return False
            msg = MessageChain.fromJsonList(obj['messageChain'])
            quote = msg.getId()
            group = obj['sender']['group']['id']
            # 打印群聊日志
            Log.info(msg=f"[GroupMessage][(SourceID){quote}][(UID){sender} -> (GID){group}] " + msg.asSerializationString())
            if not self.monitors.process(
                    type='GroupMessage', msg=msg, target=sender, group=group):
                # 如果没有触发一次性监听,则执行插件
                self.processor.group_msg_process(
                    msg=msg, group=group, target=sender, quote=quote)
            return
        if obj['type'] == 'FriendMessage':
            # 私聊
            sender = obj["sender"]["id"]
            if str(sender) in self.banList:
                # banlist过滤
                return False
            msg = MessageChain.fromJsonList(obj['messageChain'])
            quote = msg.getId()
            # 打印私聊日志
            Log.info(msg=f"[FriendMessage][(SourceID){quote}][(UID){sender}] "+msg.asSerializationString())
            if not self.monitors.process(type='FriendMessage', msg=msg, target=sender):
                self.processor.friend_msg_process(
                    msg=msg, target=sender, quote=quote)
            return

        if obj['type'] in ['GroupRecallEvent', 'MemberJoinEvent', 'MemberLeaveEventKick', 'MemberLeaveEventQuit', 'MemberCardChangeEvent']:
            # 群变化事件
            return False
