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

    def getRandomPic(self):
        t = (datetime.datetime.today()-datetime.timedelta(days=3)).date()
        rs = self.query("select id,title,tag,url,user,author from illust where send=0 order by random() limit 1")
        if len(rs) == 0:
            if self.initRankingPic():
                return self.getRandomPic()
            else:
                raise Exception('获取图片失败')

        row = rs[0]
        fname = f"{uuid.uuid1()}.png"
        if self.pixiv.downImg(url=row[3], path=self.directory, name=fname):
            return dict(id=row[0], title=row[1], tag=row[2], url=row[3], user=row[4], author=row[5], path=os.path.join(self.directory, fname))
        else:
            raise Exception("下载图片失败")

    def isSend(self, id: int) -> bool:
        if self.query('select send from illust where id=:id', {'id': id})[0][0] == 1:
            return True
        return False

    def setSend(self, id: int):
        return self.execute("update illust set send=1 where id=:id", {'id': id})

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
        rs_unsend = self.query("select count(*) from illust where date=:date and send=0",
                               {'date': t.strftime('%y-%m-%d')})[0][0]
        if rs_unsend > 0:
            return True
        rs_total = self.query("select count(*) from illust where date=:date", {'date': t})[0][0]
        rs = self.pixiv.getRanking(mode='day_male', date=t, offset=rs_total)
        append = []
        for r in rs:
            if not self.exists('illust', 'id', r[0]):
                append.append(r)
        return self.execute(
            "insert into illust (id,title,url,tag,user,author,date) values(?,?,?,?,?,?,?)", append)

    def __initSqlite(self):
        rs = self.query(
            "select name from sqlite_master where type='table' order by name")
        if ('illust',) not in rs:
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
            print('创建表illust成功')
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
            print('创建表follow成功')
