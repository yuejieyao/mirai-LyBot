from apscheduler.schedulers.background import BackgroundScheduler
from modules.dataSource.miraiDataSource import MiraiDataSource
from modules.utils import log as Log
from datetime import datetime


class MiraiScheduleProcessor:
    schedules_names = []
    schedules = {}  # 群插件

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db = MiraiDataSource()
        self.__initPluginData()
        self.db.close()

    _sched = BackgroundScheduler()

    def start(self):
        self._sched.start()

    @classmethod
    def mirai_schedule_plugin_every_minute_register(cls, schedule_name, interval: int = 1):
        """ 每隔N分钟执行
        Param:
            interval (int):  间隔分钟数,默认1分钟
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='interval', seconds=60*interval)
            cls.schedules.update({schedule_name: plugin})
            cls.schedules_names.append(schedule_name)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_every_hour_register(cls, schedule_name, interval: int = 1):
        """ 每隔N小时执行
        Param:
            interval (int):  间隔小时数,默认1小时
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='interval', seconds=60*60*interval)
            cls.schedules.update({schedule_name: plugin})
            cls.schedules_names.append(schedule_name)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_everyday_register(cls, schedule_name, hour: int, minute: int):
        """ 每天定时执行
        Param:
            days (int): 隔几天,1就是每天
            time (str): 时间字符串,如 16:45
        """

        def wapper(plugin):
            cls._sched.add_job(func=plugin().process, trigger='cron', hour=hour, minute=minute)
            cls.schedules.update({schedule_name: plugin})
            cls.schedules_names.append(schedule_name)
            return plugin
        return wapper

    def mirai_schedule_plugin_timing_register(self, run_date: datetime, func):
        """ 动态添加定时任务,只执行一次
        Param:
            run_date (datetime): 执行时间
            func (function): 执行任务函数
        """
        self._sched.add_job(func=func, trigger='date', run_date=run_date)

    def __initPluginData(self):
        """初始化插件数据库,用于功能开关和说明等需求"""

        # 删除已经不存在的插件
        schedule_register_names = self.db.query('select register_name from schedule')
        for row in schedule_register_names:
            if row[0] not in self.schedules_names:
                self.db.removeSchedule(register_name=row[0])
                Log.info(msg=f'remove schedule success : register_name = {row[0]}')

        # 增加或更新插件
        Log.info(msg='checking schedules datasource...')
        for register_name in self.schedules_names:
            self.db.addSchedule(register_name=register_name,
                              name=self.schedules[register_name].NAME, description=self.schedules[register_name].DESCRIPTION)
        Log.info(msg='check schedules datasource success')
