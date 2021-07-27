import time
import schedule


class MiraiScheduleProcessor:
    def mirai_schedule_plugins_process(self):
        schedule.run_pending()
        time.sleep(1)

    @classmethod
    def mirai_schedule_plugin_every_minute_register(cls, interval: int = 1):
        """ 每隔N分钟执行
        Param:
            interval (int):  间隔分钟数,默认1分钟
        """

        def wapper(plugin):
            schedule.every(interval).minutes.do(plugin().process)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_every_hour_register(cls, interval: int = 1):
        """ 每隔N小时执行
        Param:
            interval (int):  间隔小时数,默认1小时
        """

        def wapper(plugin):
            schedule.every(interval).hours.do(plugin().process)
            return plugin
        return wapper

    @classmethod
    def mirai_schedule_plugin_everyday_register(cls, days: int, time: str):
        """ 每N天定时执行
        Param:
            days (int): 隔几天,1就是每天
            time (str): 时间字符串,如 16:45
        """

        def wapper(plugin):
            schedule.every(days).day.at(time).do(plugin().process)
            return plugin
        return wapper
