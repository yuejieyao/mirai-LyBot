from modules.utils.sqlCombiner import Sqlite
from modules.utils import log as Log
from .JDPriceUtils import JDPriceUtils
from datetime import datetime
from modules.utils.common import get_cut_str
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import requests
import uuid


class DataSource(Sqlite):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.utils = JDPriceUtils()
        self.__initSqlite()

    def addFollow(self, goods_id: int, group: int, qq: int):
        _, title, url_goods, url_img = self.utils.getGoodsInfo(goods_id)
        return self.execute("insert into follow (jd_goods_id,title,url_img,url_goods,group_id,qq_id) values(?,?,?,?,?,?)", [
            (goods_id, title, url_goods, url_img, group, qq)])

    def getFollow(self, group: int, qq: int):
        """return List[( id, title )]"""
        res = self.query("select jd_goods_id,title from follow where group_id=:group and qq_id=:qq",
                         {'group': group, 'qq': qq})
        return res

    def removeFollow(self, goods_id: int, group: int, qq: int):
        return self.execute('delete from follow where jd_goods_id=:goods_id and group_id=:group and qq_id=:qq', {'goods_id': goods_id, 'group': group, 'qq': qq})

    def existsFollow(self, goods_id: int, group: int, qq: int):
        res = self.query(
            'select * from follow where jd_goods_id=:goods_id and group_id=:group and qq_id=:qq', {'goods_id': goods_id, 'group': group, 'qq': qq})
        if len(res) > 0:
            return True
        else:
            return False

    def getPrice(self, goods_id: int):
        """ return (price,price_plus,discont,coupon) """
        _, price, price_plus, discont, coupon = self.utils.getGoodsPrice(goods_id)
        t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.execute("insert into price (jd_goods_id,date,price,price_plus,discont,coupon) values(?,?,?,?,?,?)", [
                     (goods_id, t, price, price_plus, discont, coupon)])
        return (price, price_plus, discont, coupon)

    def isPriceChange(self, goods_id: int) -> bool:
        last = self.query(
            "select price,price_plus,discont,coupon from price where jd_goods_id=:goods_id order by date desc limit 1", {'goods_id': goods_id})[0]
        _, price, price_plus, discont, coupon = self.utils.getGoodsPrice(goods_id)
        if (price != float(last[0]) or price_plus != float(last[1])
                or discont != str(last[2]) or coupon != str(last[3])):
            return True
        else:
            return False

    def getFollowedGoods(self):
        rs = self.query("select jd_goods_id from follow group by jd_goods_id")
        return [i[0] for i in rs]

    def getFollowedUsers(self, goods_id: int):
        rs = self.query("select group_id,qq_id from follow where jd_goods_id=:goods_id", {'goods_id': goods_id})
        return rs

    def create_current_img(self, goods_id: int):
        """return (goods_url,img_path)"""
        _, title, url_goods, thumb_url = self.utils.getGoodsInfo(goods_id)
        price, price_plus, discont, coupon = self.getPrice(goods_id)

        info_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 26)
        info_color = "#474747"
        bg_color = "#F5F5F7"

        h_thumb = 350
        title = '\n'.join(get_cut_str(title, 55))
        w_title, h_title = info_font.getsize_multiline(title)

        s_price = f"当前价格: {price}"
        if price_plus:
            s_price = s_price+"\n"+f"Plus会员价格: {price_plus}"
        w_price, h_price = info_font.getsize_multiline(s_price)
        discont = '\n'.join(["优惠信息:"]+get_cut_str(discont, 30))
        w_discont, h_discont = info_font.getsize_multiline(discont)
        coupon = ("可领券:\n"+coupon) if coupon else "当前没有可领取的优惠券"
        w_coupon, h_coupon = info_font.getsize_multiline(coupon)
        width = max(w_price, w_discont, w_coupon)+350+10
        if width < w_title:
            width = w_title
        height = h_title+15+(350 if sum([h_price+h_discont+h_coupon]) < 350 else sum([h_price+h_discont+h_coupon]))

        img_new = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img_new)
        draw.text((5, 5), title, info_color, info_font)
        draw.text((5+h_thumb, 10+h_title), s_price, info_color, info_font)
        draw.text((5+h_thumb, 10+h_title+h_price), discont, info_color, info_font)
        draw.text((5+h_thumb, 10+h_title+h_price+h_discont), coupon, info_color, info_font)

        thumb = Image.open(BytesIO(requests.get(url=thumb_url, headers=self.utils.headers).content))
        thumb.convert('RGB')
        img_new.paste(thumb, (5, 10+h_title))

        path = f'modules/resource/temp/{uuid.uuid1()}.png'
        img_new.save(path)
        return (url_goods, path)

    def __initSqlite(self):
        if not self.exists_table('follow'):
            # 字段send=0表示可发送,1表示各种原因屏蔽掉不发送
            self.execute("""
                create table follow
                (
                    id INTEGER PRIMARY KEY,
                    jd_goods_id text,
                    title text,
                    url_img text,
                    url_goods text,
                    group_id int,
                    qq_id int
                )
            """)
            Log.info('[Plugin][JDPrice] create table follow success')
        if not self.exists_table('price'):
            self.execute("""
                create table price
                (
                    id INTEGER PRIMARY KEY,
                    jd_goods_id text,
                    date date,
                    price real,
                    price_plus real,
                    discont text,
                    coupon text
                )
            """)
            Log.info('[Plugin][JDPrice] create table price success')
