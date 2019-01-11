# coding=utf-8
from urllib import request
import pymongo
import json
import time
import requests
from fake_useragent import UserAgent

MONGO_DB = 'taobao'
MONGO_COLLECTION = 'phone'
COLLECTION = None


# 获取响应
def get_response(url):
    ua = UserAgent()
    headers = {
        "user-agent": ua.random,
        "referer": "https://item.jd.com/100001364184.html",
        "cookie": "__jdc=122270672; __jdu=1998043716; shshshfpa=0b76cc70-a07b-43f0-18d1-9c54696148d0-1546923852; user-key=5eed6624-9d44-4c3c-a666-a5e168a3c97c; cn=0; shshshfpb=l9p%2Fek%2F9%20j8Zezw%20Kh3FEcw%3D%3D; JSESSIONID=1A9CC00D625F73880211F15CF008B877.s1; unpl=V2_ZzNtbUpSQR1yDE5Qfx0MBGIEEw5LV0JCIQBPXHkYXQU1AhEOclRCFX0UR1RnGFUUZwYZXENcQR1FCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHsRVAxmBhBbQlBzJXI4dmRzHlQNbgEiXHJWc1chVE5WeRpUAioDGlVLVkYXcwhBZHopXw%3d%3d; __jda=122270672.1998043716.1546403111.1546923830.1546927240.2; __jdv=122270672|baidu-pinzhuan|t_288551095_baidupinzhuan|cpc|0f3d30c8dba7459bb52f2eb5eba8ac7d_0_9439659555a0460b810fe9893001c02b|1546927239725; PCSYCityID=1607; ipLoc-djd=1-72-4137-0; areaId=1; _gcl_au=1.1.1625722664.1546927248; 3AB9D23F7A4B3C9B=Z7HGYM5TUSHOFPPVYSM6SOLRAYJ54HRI76WB3EHEKXYX5H2NXEV6JK7O53O55CQ6R6QVMEPMGHRTUISW7RXAKJGUQA; shshshfp=6ae62b93af975b490a6692bf0ea759b5; shshshsID=f7e1156f0f0cd3072dd4afa1fa8e9391_3_1546927360412; __jdb=122270672.6.1998043716|2.1546927240"
    }
    rs = request.Request(url=url, headers=headers, method='GET')
    response = request.urlopen(rs)
    time.sleep(1)
    html = response.read().decode('GBK').split('(', 1)[1][:-2]
    result = json.loads(html)
    return result


def get_maxpage(url):
    js = get_response(url)
    return js['maxPage']


def dbsave(data):
    comments = data['comments']
    for ls in comments:
        datadir = {
            'id': ls['id'],
            'content': ls['content'],
            'createTime': ls['creationTime'],
            'color': ls['productColor'],
            'productSize': ls['productSize'],
            'userLevelName': ls['userLevelName'],
            'productSales': ls['productSales'][0]['saleValue'],
            'usefulVoteCount': ls['usefulVoteCount']
        }
        if COLLECTION.update({'id': ls['id']}, {'$set': datadir}, True):
            print('保存成功', datadir)
        else:
            print('保存失败', datadir)


def main():
    url = "https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv2724&productId=100001364210&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1"
    page = get_maxpage(url)
    for i in range(page):
        curpageurl = url.replace('page=0', 'page={}'.format(i))
        data = get_response(curpageurl)
        dbsave(data)
        time.sleep(2)


if __name__ == '__main__':
    con = pymongo.MongoClient(host='localhost', port=27017)
    COLLECTION = con[MONGO_DB][MONGO_COLLECTION]
    main()
    con.close()
    # email()
