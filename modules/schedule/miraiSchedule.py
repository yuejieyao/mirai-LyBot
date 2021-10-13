from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime


class MiraiScheduleProcessor:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    _sched = BackgroundScheduler()

    def start(self):
        self._sched.start()

    @classmethod
    def mirai_schedule_plugin_every_minute_register(cls, interval: int = 1):
        """ 每隔N分钟执行
        Param:
            interval (int):  间隔分钟数,默认1分钟
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='interval', seconds=60*interval)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_every_hour_register(cls, interval: int = 1):
        """ 每隔N小时执行
        Param:
            interval (int):  间隔小时数,默认1小时
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='interval', seconds=60*60*interval)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_everyday_register(cls, hour: int, minute: int):
        """ 每天定时执行
        Param:
            days (int): 隔几天,1就是每天
            time (str): 时间字符串,如 16:45
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='cron', hour=hour, minute=minute)
            return plugin
        return wapper

    def mirai_schedule_plugin_timing_register(self, run_date: datetime, func, args=None):
        """ 动态添加定时任务,只执行一次
        Param:
            run_date (datetime): 执行时间
            func (function): 执行任务函数
            args : 执行函数参数
        """

        self._sched.add_job(func=func, trigger='date', run_date=run_date, args=args)

# import schedule
# import time
# class MiraiScheduleProcessor:
#     def mirai_schedule_plugins_process(self):
#         schedule.run_pending()

#         # 立刻执行一次,并每隔1分钟执行一次,测试用
#         # schedule.run_all(delay_seconds=60)
#         time.sleep(1)

#     @classmethod
#     def mirai_schedule_plugin_every_minute_register(cls, interval: int = 1):
#         """ 每隔N分钟执行
#         Param:
#             interval (int):  间隔分钟数,默认1分钟
#         """

#         def wapper(plugin):
#             schedule.every(interval).minutes.do(plugin().process)
#             return plugin
#         return wapper

#     @classmethod
#     def mirai_schedule_plugin_every_hour_register(cls, interval: int = 1):
#         """ 每隔N小时执行
#         Param:
#             interval (int):  间隔小时数,默认1小时
#         """

#         def wapper(plugin):
#             schedule.every(interval).hours.do(plugin().process)
#             return plugin
#         return wapper

#     @classmethod
#     def mirai_schedule_plugin_everyday_register(cls, days: int, time: str):
#         """ 每N天定时执行
#         Param:
#             days (int): 隔几天,1就是每天
#             time (str): 时间字符串,如 16:45
#         """

#         def wapper(plugin):
#             schedule.every(days).day.at(time).do(plugin().process)
#             return plugin
#         return wapper
