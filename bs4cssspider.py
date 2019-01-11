# coding=utf-8
import requests
import pymongo
from bs4 import BeautifulSoup as bfsoup
import time
from fake_useragent import UserAgent

MONGO_DB = 'House'
MONGO_COLLECTION = 'fangtianxia'
COLLECTION = None


# 获取本地测试数据
def get_data():
    with open('data.html', 'r', encoding='utf-8') as f:
        rs = f.read()
    return rs


# 获取响应
def get_response(url):
    ua = UserAgent()
    headers = {
        "user-agent": ua.random,
        "referer": "https://item.jd.com/100001364184.html",
        "cookie": "global_cookie=ubszpzxe3seqe0ixpdh4qmozw10jqq1d161; unique_cookie=U_ubszpzxe3seqe0ixpdh4qmozw10jqq1d161*3"
    }
    response = requests.get(url=url, headers=headers)
    html = response.content.decode('gb18030')
    return html


# 保存数据
def save_data(data):
    if COLLECTION.update_one({'url': data['url']}, {'$set': data}, True):
        print("successful:{}".format(str(data)))
    else:
        print('fail:{}'.format(str(data)))


# 匹配提取数据
def matchdata(data):
    soup = bfsoup(data, 'html.parser')
    houselist = soup.select('div.houseList .list.rel')
    for house in houselist:
        no = len(house.select('span.dj .no2'))
        half = len(house.select('span.dj .half'))
        address = house.select('dd p')[1]
        pricediv = house.select('p.priceAverage span')
        ratio = house.select('p.ratio span')
        rs = {
            'url': house.select("dd p a")[0]['href'],
            'name': house.select("dd p a")[0].string,
            'score': 5 - no - 0.5 * half,
            'area': address.select('a')[0].get_text(),
            'business': address.select('a')[1].get_text(),
            'address': address.get_text().strip().split('\n')[-1].strip(),
            'buildyear': house.select('ul li')[-1].get_text()[:-3],
            'sallprice': pricediv[0].get_text() if len(pricediv) > 0 else 0,
            'ratio': ratio[0].get_text() if len(ratio) > 0 else 0
        }
        save_data(rs)


# 主程序流程
def main():
    maxpage = 100
    url = "https://sz.esf.fang.com/housing/__0_0_0_0_{}_0_0_0/"
    for i in range(0, maxpage + 1):
        curpageurl = url.format(str(i))
        data = get_response(curpageurl)
        # data = get_data()
        matchdata(data)
        time.sleep(2)


# 启动入口
if __name__ == '__main__':
    con = pymongo.MongoClient(host='localhost', port=27017)
    COLLECTION = con[MONGO_DB][MONGO_COLLECTION]
    main()
    con.close()
