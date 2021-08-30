from modules.utils.sqlCombiner import Sqlite
from .pixivUtils import PixivUtils
import os
import datetime
import uuid


class DataSource(Sqlite):
    directory = "modules/resource/illusts"

    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.__initSqlite()
        self.pixiv = PixivUtils()
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def getRandomPic(self, group: int):
        # t = (datetime.datetime.today()-datetime.timedelta(days=3)).date()
        rs = self.query("""
            select i.id,i.title,i.tag,i.url,i.user,i.author
            from illust i
            where send=0
            and not exists(select * from send s where s.pic_id=i.id and s.send_group=?)
            order by random() limit 1""", (group,))
        if len(rs) == 0:
            if self.initRankingPic():
                return self.getRandomPic(group=group)
            else:
                raise Exception('获取图片失败')

        row = rs[0]
        fname = f"{uuid.uuid1()}.png"
        if self.pixiv.downImg(url=row[3], path=self.directory, name=fname):
            return dict(id=row[0], title=row[1], tag=row[2], url=row[3], user=row[4], author=row[5], path=os.path.join(self.directory, fname))
        else:
            raise Exception("下载图片失败")

    def isSend(self, id: int, group: int) -> bool:
        if self.query('select count(*) from send where pic_id=:pic_id and send_group=:send_group', {'pic_id': id, 'send_group': group})[0][0] > 0:
            return True
        return False

    def setSend(self, id: int, group: int):
        return self.execute("insert into send (pic_id,send_group) values(?,?)", [(id, group)])

    def getNewPic(self, user: int):
        illust = self.pixiv.getUserPic(user=user)[0]
        if not self.exists(table='illust', column='id', value=illust[0]):
            self.execute(
                "insert into illust (id,title,url,tag,user,author,date) values(?,?,?,?,?,?,?)", illust)
        fname = f"{uuid.uuid1()}.png"
        if self.pixiv.downImg(url=illust[2], path=self.directory, name=fname):
            return dict(id=illust[0], title=illust[1], tag=illust[3], url=illust[2], user=illust[4], author=illust[5], path=os.path.join(self.directory, fname))
        else:
            raise Exception("下载图片失败")

    def follow(self, user: int, group: int, qq: int):
        if self.pixiv.getUserIsvalid(user=user):
            if self.query("select count(*) from follow where author_id=:author_id and follow_group=:follow_group and follow_qq=:follow_qq", {'author_id': user, 'follow_group': group, 'follow_qq': qq})[0][0] > 0:
                raise Exception(f'群号:{group} qq号:{qq} 作者: {user} 已关注,请勿重复关注')
            return self.execute("insert into follow (author_id,follow_group,follow_qq) values(?,?,?)", [(user, group, qq)])
        else:
            raise Exception('作者ID无效')

    def unfollow(self, user: int, group: int, qq: int):
        rs = self.query("select follow_id from follow where author_id=:author_id and follow_group=:follow_group and follow_qq=:follow_qq",
                        {'author_id': user, 'follow_group': group, 'follow_qq': qq})
        if len(rs) == 0:
            raise Exception('你并没有关注该作者')
        else:
            return self.execute("delete from follow where follow_id=:follow_id", {'follow_id': rs[0][0]})

    def getFollowAuthorIds(self):
        rs = self.query("select author_id from follow group by author_id")
        return [i[0] for i in rs]

    def getFollowers(self, user: int):
        """list[follow_group,follow_qq]"""
        return self.query("select follow_group,follow_qq from follow where author_id=:author_id", {'author_id': user})

    def initRankingPic(self) -> bool:
        t = (datetime.datetime.today()-datetime.timedelta(days=3)).date()
        # rs_unsend = self.query("select count(*) from illust where date=:date and send=0",
        #                        {'date': t.strftime('%y-%m-%d')})[0][0]
        # if rs_unsend > 0:
        #     return True
        rs_total = self.query("select count(*) from illust where date=:date", {'date': t.strftime('%y-%m-%d')})[0][0]
        # 由于日榜会有大量和之前日期重复的图,直接count日期得到的数量是不正确的,这里偷懒直接循环了
        append = []
        jump = 10
        i = 0
        while len(append) == 0:
            offset = int(rs_total+(i*jump))
            if offset >= 500:
                # 日榜最多500
                return False
            rs = self.pixiv.getRanking(mode='day_male', date=t, offset=offset)
            for r in rs:
                if not self.exists('illust', 'id', r[0]):
                    append.append(r)
            i = i+1
        self.execute(
            "insert into illust (id,title,url,tag,user,author,date) values(?,?,?,?,?,?,?)", append)
        # 屏蔽榜单上的漫画
        self.execute("update illust set send=1 where title like '%漫画%' or tag like '%漫画%'")
        self.execute("update illust set send=1 where title like '%4コマ%' or tag like '%4コマ%'")
        self.execute("update illust set send=1 where title like '%まんが%' or tag like '%まんが%'")
        return True

    def __initSqlite(self):
        rs = self.query(
            "select name from sqlite_master where type='table' order by name")
        if ('illust',) not in rs:
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table illust
                (
                    pic_id INTEGER PRIMARY KEY,
                    id int UNIQUE,
                    title text,
                    tag text,
                    url text,
                    user int,
                    author text,
                    date date,
                    send int DEFAULT 0
                )
            """)
            print('Pixiv插件:创建表illust成功')
        if ('follow',) not in rs:
            self.execute("""
                create table follow
                    (
                        follow_id INTEGER PRIMARY KEY,
                        author_id int,
                        follow_group int,
                        follow_qq int
                    )
            """)
            print('Pixiv插件:创建表follow成功')
        if ('send',) not in rs:
            # 发送记录
            self.execute("""
                create table send
                    (
                        send_id INTEGER PRIMARY KEY,
                        pic_id int,
                        send_group int
                    )
            """)
            print('Pixiv插件:创建表send成功')
