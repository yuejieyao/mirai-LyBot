from lxml import etree
import requests


class JDPriceUtils:
    def __init__(self) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
        }

    def getGoodsInfo(self, goods_id: int):
        """return (id,title,url_goods,url_img)"""
        url_goods = f"http://item.jd.com/{goods_id}.html"
        resp = requests.get(url=url_goods, headers=self.headers)
        resp.encoding = 'utf-8'
        resp.raise_for_status()
        page = etree.HTML(resp.text)
        title = page.xpath('//div[@class="itemInfo-wrap"]/div[@class="sku-name"]/text()')
        title = ''.join(title).replace('\n', '').strip()
        img = 'https:'+page.xpath('//img[@id="spec-img"]/@data-origin')[0]
        return (goods_id, title, url_goods, img)

    def getGoodsPrice(self, goods_id: int):
        """return (id,price,price_plus,discont,coupon)"""
        url_goods = f"https://item-soa.jd.com/getWareBusiness?skuId={goods_id}"
        resp = requests.get(url=url_goods, headers=self.headers)
        resp.encoding = 'utf-8'
        resp.raise_for_status()
        json = resp.json()
        price = float(json['price']['p'])
        price_plus = float(json['price']['pp']) if json['price']['pp'] else 0
        discont = '\n'.join([i['value'] for i in json['promotion']['activity']]) if 'promotion' in json else ''
        coupon = '\n'.join(f"满{i['quota']}减{i['discount']}" for i in json['couponInfo']
                           ) if 'couponInfo' in json else ''
        return (goods_id, price, price_plus, discont, coupon)

    
