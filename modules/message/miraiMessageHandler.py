from modules.conf import config
from modules.events.miraiEvent import MiraiEventProcessor
from modules.message.messageChain import MessageChain
from modules.message.miraiMessageMonitorHandler import MiraiMessageMonitorHandler
from modules.plugins.miraiPlugin import MiraiMessagePluginProcessor
from modules.utils import log


class MiraiMessageHandler:
    def __init__(self) -> None:
        self.processor = MiraiMessagePluginProcessor()
        self.monitors = MiraiMessageMonitorHandler()
        self.events = MiraiEventProcessor()
        self.banList = config.getConf('mirai', 'banList').split(',')
        self.prev = {}

    def onMessage(self, obj):
        """ 根据websocket传来的mirai message触发各种事件 """
        if 'type' not in obj:
            # 未知消息
            return

        if obj['type'] == 'GroupMessage':
            # 群消息
            sender = obj["sender"]["id"]
            if str(sender) in self.banList:
                # banlist过滤
                return
            msg = MessageChain.fromJsonList(obj['messageChain'])
            quote = msg.getId()
            group = obj['sender']['group']['id']

            # 上一条信息
            if group in self.prev:
                msg.setPrev(self.prev[group])
            self.prev[group] = msg

            # 打印群聊日志
            log.info(
                msg=f"[GroupMessage][(SourceID){quote}][(UID){sender} -> (GID){group}] " + msg.asSerializationString())
            if not self.monitors.process(monitor_type='GroupMessage', msg=msg, target=sender, group=group):
                # 如果没有触发一次性监听,则执行插件
                self.processor.group_msg_process(msg=msg, group=group, target=sender, quote=quote)
            return
        if obj['type'] == 'FriendMessage':
            # 私聊
            sender = obj["sender"]["id"]
            if str(sender) in self.banList:
                # banlist过滤
                return
            msg = MessageChain.fromJsonList(obj['messageChain'])
            quote = msg.getId()
            # 打印私聊日志
            log.info(msg=f"[FriendMessage][(SourceID){quote}][(UID){sender}] " + msg.asSerializationString())
            if not self.monitors.process(monitor_type='FriendMessage', msg=msg, target=sender):
                self.processor.friend_msg_process(msg=msg, target=sender, quote=quote)
            return
        if obj['type'] == "TempMessage":
            # 群临时消息
            sender = obj["sender"]["id"]
            if str(sender) in self.banList:
                # banlist过滤
                return
            msg = MessageChain.fromJsonList(obj['messageChain'])
            quote = msg.getId()
            group = obj['sender']['group']['id']
            log.info(
                msg=f"[TempMessage][(SourceID){quote}][(UID){sender} -> (GID){group}] " + msg.asSerializationString())
            if not self.monitors.process(monitor_type='TempMessage', msg=msg, group=group, target=sender):
                self.processor.temp_msg_process(msg=msg, group=group, target=sender, quote=quote)
            return

        if obj['type'] in ['GroupRecallEvent',
                           'MemberJoinEvent',
                           'MemberLeaveEventKick',
                           'MemberLeaveEventQuit',
                           'MemberCardChangeEvent',
                           'MemberPermissionChangeEvent',
                           'MemberMuteEvent']:
            log.info(msg=f"[{obj['type']}] Event Occurred")
            self.events.mirai_events_process(obj)
            return
