from threading import Thread


class MiraiEventProcessor:
    # 新人进群
    mirai_join_events_names = []
    mirai_join_events = {}
    # 群消息撤回
    mirai_group_recalls_names = []
    mirai_group_recalls = {}
    # 群名片改动
    mirai_member_card_change_events_names = []
    mirai_member_card_change_events = {}
    # 群成员权限改变
    mirai_member_permission_change_events_names = []
    mirai_member_permission_change_events = {}
    # 群成员被禁言
    mirai_member_mute_events_names = []
    mirai_member_mute_events = {}

    def mirai_events_process(self, obj):
        if obj['type'] == 'MemberJoinEvent':
            qq = obj['member']['id']
            group = obj['member']['group']['id']
            name = obj['member']['memberName']
            for event_name in self.mirai_join_events_names:
                Thread(self.mirai_join_events[event_name]().process(group, qq, name)).start()
        elif obj['type'] == 'GroupRecallEvent':
            qq = obj['authorId']
            message_id = obj['messageId']
            group = obj['group']['id']
            for event_name in self.mirai_group_recalls_names:
                Thread(self.mirai_group_recalls[event_name]().process(group, qq, message_id)).start()
        elif obj['type'] == 'MemberCardChangeEvent':
            group = obj['member']['group']['id']
            qq = obj['member']['id']
            name_old = obj['origin']
            name_new = obj['current']
            for event_name in self.mirai_member_card_change_events_names:
                Thread(self.mirai_member_card_change_events[event_name]
                       ().process(group, qq, name_old, name_new)).start()
        elif obj['type'] == 'MemberPermissionChangeEvent':
            group = obj['member']['group']['id']
            qq = obj['member']['id']
            permission_old = obj['origin']
            permission_new = obj['current']
            for event_name in self.mirai_member_permission_change_events_names:
                Thread(self.mirai_member_permission_change_events[event_name]().process(
                    group, qq, permission_old, permission_new)).start()
        elif obj['type'] == 'MemberMuteEvent':
            group = obj['member']['group']['id']
            qq_member = obj['member']['id']
            qq_operator = obj['operator']['id']
            seconds = obj['durationSeconds']
            for event_name in self.mirai_member_mute_events_names:
                Thread(self.mirai_member_mute_events[event_name]().process(
                    group, qq_member, qq_operator, seconds)).start()

    @classmethod
    def mirai_join_event_register(cls, event_name):
        """新进群员事件注册"""

        def wrapper(event):
            cls.mirai_join_events.update({event_name: event})
            cls.mirai_join_events_names.append(event_name)
            return event

        return wrapper

    @classmethod
    def mirai_group_recall_register(cls, event_name):
        """群消息撤回事件注册"""

        def wrapper(event):
            cls.mirai_group_recalls.update({event_name: event})
            cls.mirai_group_recalls_names.append(event_name)
            return event

        return wrapper

    @classmethod
    def mirai_member_card_change_event_register(cls, event_name):
        """群名片改动事件注册"""

        def wrapper(event):
            cls.mirai_member_card_change_events.update({event_name: event})
            cls.mirai_member_card_change_events_names.append(event_name)
            return event

        return wrapper

    @classmethod
    def mirai_member_permission_change_event_register(cls, event_name):
        """群员权限改动事件注册"""

        def wrapper(event):
            cls.mirai_member_permission_change_events.update({event_name: event})
            cls.mirai_member_permission_change_events_names.append(event_name)
            return event

        return wrapper

    @classmethod
    def mirai_member_mute_event_register(cls, event_name):
        """群成员被禁言事件注册"""

        def wrapper(event):
            cls.mirai_member_mute_events.update({event_name: event})
            cls.mirai_member_mute_events_names.append(event_name)
            return event

        return wrapper
