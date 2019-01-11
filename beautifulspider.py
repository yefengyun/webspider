# coding=utf-8
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import os
import time


def getresponse(url):
    ua = UserAgent()
    headers = {
        'user-agent': ua.random
    }
    responses = requests.get(url=url, headers=headers)
    return responses.content.decode(responses.encoding)


def matchsavedata(data, file):
    bfs = BeautifulSoup(data, 'lxml')
    for i in bfs.dl.children:
        rslist = []
        if len(str(i).strip()) != 0:
            bfsc = BeautifulSoup(str(i), 'lxml')
            rslist.append(bfsc.i.string)
            rslist.append(bfsc.find(class_='board-img')['data-src'])
            rslist.append(bfsc.find(class_='name').a.string)
            rslist.append(bfsc.find(class_='star').string.strip().split("：")[-1].replace(',', '/'))
            rslist.append(bfsc.find(class_='integer').string.strip() + bfsc.find(class_='fraction').string.strip())
            file.write(','.join(rslist) + '\n')


def main():
    if not os.path.exists('data'):
        os.mkdir('data')

    f = open('data/movie.cvs', 'a', encoding='utf-8')
    f.write('排名,图像链接,影片名称,演员,上映事件,评分\n')
    url = "https://maoyan.com/board/4?offset="
    for i in range(10):
        endurl = url + str(i * 10)
        html = getresponse(endurl)
        matchsavedata(html, f)
        time.sleep(2)

    f.close()


if __name__ == '__main__':
    main()
