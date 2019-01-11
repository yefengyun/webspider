import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

UA = UserAgent()
CHROME = UA.chrome
COOKIES = "Hm_lvt_63a864f136a45557b3e0cbce07b7e572=1547111105,1547111561; Hm_lpvt_63a864f136a45557b3e0cbce07b7e572=1547111618"

if __name__ == '__main__':
    endurl = 'https://www.27270.com/ent/meinvtupian/2018/307639_9.html'
    headers = {
        'Cookie': COOKIES,
        'UserAgent': CHROME
    }
    rp = requests.get(url=endurl, headers=headers)
    # print(rp.text)
    try:
        bs = BeautifulSoup(rp.text.replace('</font></span><br />', ''), 'html.parser')
        imgurl = bs.select('div#picBody img')[0]['src']
    except IndexError:
        try:
            bs = BeautifulSoup(rp.text.replace('</font></span></span><br />', ''), 'html.parser')
            imgurl = bs.select('div#picBody img')[0]['src']
        except Exception:
            imgurl = 'none'

    print(imgurl)
