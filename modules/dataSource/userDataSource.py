from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log
import datetime
import random


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()

    def isSign(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        if self.query('select count(*) from sign where user_qq=:user_qq and date=:date', {'user_qq': qq, 'date': t})[0][0] == 1:
            return True
        return False

    def sign(self, qq: int, sign_text: str):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.execute('insert into sign (user_qq,date,sign_text) values(?,?,?)', [(qq, t, sign_text)])

    def isOver(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        if self.query('select count(*) from lottery where user_qq=:user_qq and date=:date', {'user_qq': qq, 'date': t})[0][0] >= 3:
            return True
        return False

    def has_user(self, qq: int):
        if self.query('select count(*) from user where user_qq=:user_qq', {'user_qq': qq})[0][0] == 1:
            return True
        return False

    def count_lottery_today(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.query('select count(*) from lottery where user_qq=:user_qq and date=:date', {'user_qq': qq, 'date': t})[0][0]

    def buy(self, qq: int, group: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        content = f"{random.randint(1,16)},{random.randint(1,16)},{random.randint(1,16)},{random.randint(1,16)},{random.randint(1,16)},{random.randint(1,16)},{random.randint(1,8)}"
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
            return self.execute('update user set money=money+:money where user_qq=:user_qq', {'money': money, 'user_qq': qq})
        else:
            return self.execute('insert into user (user_qq,money) values(?,?)', [(qq, money)])

    def min_money(self, qq: int, money: int):
        if self.has_user(qq=qq):
            if self.get_money(qq=qq) >= money:
                return self.execute('update user set money=money-:money where user_qq=:user_qq', {'money': money, 'user_qq': qq})
        return False

    def get_lottery_today(self, qq: int):
        t = datetime.datetime.today().date().strftime('%y-%m-%d')
        return self.query('select content from lottery where user_qq=:user_qq and date=:date', {'user_qq': qq, 'date': t})

    def get_lottery_yesterday_group_qq(self, group: int, qq: int):
        t = (datetime.datetime.today()-datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        return self.query('select content from lottery where date=:date and user_group=:user_group and user_qq=:user_qq', {'date': t, 'user_group': group, 'user_qq': qq})

    def get_lottery_yesterday_group(self):
        t = (datetime.datetime.today()-datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        r = self.query('select user_group from lottery where date=:date group by user_group', {'date': t})
        return [int(i[0]) for i in r]

    def get_lottery_yesterday_qq(self, group: int):
        t = (datetime.datetime.today()-datetime.timedelta(days=1)).date().strftime('%y-%m-%d')
        r = self.query('select user_qq from lottery where date=:date and user_group=:user_group group by user_qq', {
                       'date': t, 'user_group': group})
        return [int(i[0]) for i in r]

    def __initSqlite(self):
        rs = self.query(
            "select name from sqlite_master where type='table' order by name")
        if ('sign',) not in rs:
            self.execute("""
                create table sign
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    date date,
                    sign_text text
                ) 
            """)
        if ('user',) not in rs:
            self.execute("""
                create table user
                (
                    id INTEGER PRIMARY KEY,
                    user_qq int,
                    money int DEFAULT 0
                ) 
            """)
        if ('lottery',) not in rs:
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
