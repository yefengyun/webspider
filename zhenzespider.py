# coding=utf-8
import requests
from fake_useragent import UserAgent
import re
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
    com = re.compile(
        r'<dd>.*?">(.*?)</i>.*?<img data-src="(.*?)".*?title="(.*?)".*?class="star">(.*?)</p>.*?class="releasetime">(.*?)</p>.*?class="integer">(.*?)</i>.*?class="fraction">(\d)</i>',
        re.S)
    lst = re.findall(com, data)
    for i in lst:
        datals = [i.strip().split('：')[-1].replace(',', '/') for i in i[:-2]]
        datals.append((i[-2] + i[-1]))
        string = '{}\n'.format(','.join(datals))
        file.write(string)
        print(string)


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
