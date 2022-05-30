import datetime
import random

from modules.utils import log
from modules.utils.sqlCombiner import Sqlite


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()

    def isSign(self, qq: int):
        """ 是否签到 """
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        if self.query('select count(*) from sign where user_qq=:user_qq and date=:date',
                      {'user_qq': qq, 'date': t})[0][0] == 1:
            return True
        return False

    def sign(self, qq: int, sign_text: str):
        """ 签到 """
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.execute('insert into sign (user_qq,date,sign_text) values(?,?,?)', [(qq, t, sign_text)])

    def isOver(self, qq: int):
        """ 今日购买彩票是否满3 """
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        if \
                self.query('select count(*) from lottery where user_qq=:user_qq and date=:date',
                           {'user_qq': qq, 'date': t})[0][0] >= 3:
            return True
        return False

    def has_user(self, qq: int):
        if self.query('select count(*) from user where user_qq=:user_qq', {'user_qq': qq})[0][0] == 1:
            return True
        return False

    def count_lottery_today(self, qq: int):
        """ 今天购买彩票数量 """
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return \
            self.query('select count(*) from lottery where user_qq=:user_qq and date=:date',
                       {'user_qq': qq, 'date': t})[0][0]

    def buy(self, qq: int, group: int):
        """ 买彩票 """
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        # 前6位从1-27中抽取,不重复,最后1位随机1-9
        range_l = range(1, 28)
        c = random.sample(range_l, 6)
        c.append(random.randint(1, 9))
        content = ','.join(map(str, c))
        self.execute('insert into lottery (user_qq,user_group,content,date) values(?,?,?,?)', [(qq, group, content, t)])
        return content

    def get_money(self, qq: int):
        if self.has_user(qq=qq):
            return self.query('select money from user where user_qq=:user_qq', {'user_qq': qq})[0][0]
        else:
            self.execute('insert into user (user_qq,money) values(?,?)', [(qq, 0)])
            return 0

    def add_money(self, qq: int, money: int):
        if self.query('select count(*) from user where user_qq=:user_qq', {'user_qq': qq})[0][0] == 1:
            return self.execute('update user set money=money+:money where user_qq=:user_qq',
                                {'money': money, 'user_qq': qq})
        else:
            return self.execute('insert into user (user_qq,money) values(?,?)', [(qq, money)])

    def min_money(self, qq: int, money: int):
        if self.has_user(qq=qq):
            if self.get_money(qq=qq) >= money:
                return self.execute('update user set money=money-:money where user_qq=:user_qq',
                                    {'money': money, 'user_qq': qq})
        return False

    def get_lottery_today(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.query('select content from lottery where user_qq=:user_qq and date=:date',
                          {'user_qq': qq, 'date': t})

    def get_lottery_yesterday_group_qq(self, group: int, qq: int):
        t = (datetime.datetime.today() - datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        return self.query(
            'select content from lottery where date=:date and user_group=:user_group and user_qq=:user_qq',
            {'date': t, 'user_group': group, 'user_qq': qq})

    def get_lottery_yesterday_group(self):
        t = (datetime.datetime.today() - datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        r = self.query('select user_group from lottery where date=:date group by user_group', {'date': t})
        return [int(i[0]) for i in r]

    def get_lottery_yesterday_qq(self, group: int):
        t = (datetime.datetime.today() - datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        r = self.query('select user_qq from lottery where date=:date and user_group=:user_group group by user_qq', {
            'date': t, 'user_group': group})
        return [int(i[0]) for i in r]

    def __initSqlite(self):
        if not self.exists_table('sign'):
            self.execute("""
                create table sign
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    date date,
                    sign_text text
                ) 
            """)
            log.info(msg="[Mirai][User] create table sign success")
        # 用户表
        if not self.exists_table('user'):
            self.execute("""
                create table user
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    money int DEFAULT 0
                ) 
            """)
            log.info(msg="[Mirai][User] create table user success")
        # 彩票表
        if not self.exists_table('lottery'):
            self.execute("""
                create table lottery
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    user_group int,
                    content text,
                    date date
                ) 
            """)
            log.info(msg="[Mirai][User] create table lottery success")
