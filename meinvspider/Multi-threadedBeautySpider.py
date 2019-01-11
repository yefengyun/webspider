import time
import os
import shutil
import requests
from bs4 import BeautifulSoup
import threading
from fake_useragent import UserAgent

UA = UserAgent()
IE = UA.ie
FIREFOX = UA.firefox
CHROME = UA.chrome
SAFARI = UA.safari
COOKIES = "Hm_lvt_63a864f136a45557b3e0cbce07b7e572=1547111105,1547111561,1547179992; Hm_lpvt_63a864f136a45557b3e0cbce07b7e572=1547180338"
BASEMAXPAGE = 0
BASEURL = "https://www.27270.com"
BASEPATH = os.getcwd()


# 字符转数字
def stoint(src, default=1):
    try:
        dst = int(src)
    except Exception as e:
        print('\033[1;31;47m {}\033[0m'.format(e))
        dst = default
    return dst


# 装饰器 创建目录和切换
def mkdir(fun):
    def pathch(*args, **kwargs):
        name = kwargs['title']
        abspath = os.path.join(BASEPATH, name)
        if not os.path.exists(abspath):
            os.mkdir(abspath)
            os.chdir(abspath)
        else:
            return None
        try:
            fun(*args, **kwargs)
        except Exception as e:
            print('\033[1;31;47m {}\033[0m'.format(e))
            shutil.rmtree(abspath)

    return pathch


# 获取主页相应
def get_base_response(url):
    headers = {
        'Cookie': COOKIES,
        'User-Agent': CHROME
    }
    rep = requests.get(url, headers)
    html = rep.content.decode("GBK")
    global BASEMAXPAGE
    if not BASEMAXPAGE:
        bsoup = BeautifulSoup(html, 'html.parser')
        page = bsoup.select('div.NewPages ul li a')
        BASEMAXPAGE = stoint(page[-1]['href'].split('_')[-1].split('.')[0])
    return html


# 获取主页的图片链接
def get_son_url(html):
    suop = BeautifulSoup(html, 'html.parser')
    li = suop.select('div.MeinvTuPianBox ul li')
    for i in li:
        obj = i.select('a.MMPic')[0]
        url = obj['href']
        title = obj['title']
        yield url, title


# 获取最大页数
def get_per_maxpage(url):
    headers = {
        'Cookie': COOKIES,
        'User-Agent': CHROME
    }
    rsp = requests.get(url=url, headers=headers)
    html = rsp.content.decode("GBK")
    soup = BeautifulSoup(html, 'html.parser')
    allpage = soup.select('#pageinfo')[0].attrs['pageinfo']
    return allpage


# 保存图像
@mkdir
def saveimage(url, allpage, title):
    for i in range(1, allpage + 1):
        endurl = url.replace('.html', "_{}.html".format(i))
        headers = {
            'Cookie': COOKIES,
            'UserAgent': CHROME
        }

        rp = requests.get(url=endurl, headers=headers)
        # bs = BeautifulSoup(rp.text.replace('</font></span><br />', ''), 'html.parser')
        # imgurl = bs.select('div#picBody img')[0]['src']
        try:
            bs = BeautifulSoup(rp.text.replace('</font></span><br />', ''), 'html.parser')
            imgurl = bs.select('div#picBody img')[0]['src']
        except IndexError:
            try:
                bs = BeautifulSoup(rp.text.replace('</font></span></span><br />', ''), 'html.parser')
                imgurl = bs.select('div#picBody img')[0]['src']
            except Exception:
                return 0

        rp = requests.get(url=imgurl, headers=headers)
        imgname = os.path.split(imgurl)[-1]
        with open(imgname, 'wb') as f:
            f.write(rp.content)
        print('save successful:{}/{}'.format(title, imgname))


# 获取图像
def get_image(gensonurl):
    for url, title in gensonurl:
        endurl = BASEURL + url
        print(endurl)
        title = title
        allpage = stoint(get_per_maxpage(endurl))
        saveimage(endurl, allpage, title=title)


def main():
    baseurl = "https://www.27270.com/ent/meinvtupian/"
    get_base_response(baseurl)
    url = "https://www.27270.com/ent/meinvtupian/list_11_{}.html"
    for i in range(1, BASEMAXPAGE + 1):
        endurl = url.format(i)
        html = get_base_response(endurl)
        gensonurl = get_son_url(html)
        get_image(gensonurl)


if __name__ == '__main__':
    main()
