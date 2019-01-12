import time
import pymongo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

KEYWORD = '手机'  # 要查找数据的关键词
DB = 'JD'  # 数据库
COLLECTION = 'phone'  # 集合
URL = "https://www.jd.com"  # 网址

CONN = None  # 链接
browser = None  # 声明浏览器
wait = None  # 声明显式等待时间


# 获取页数
def get_search():
    try:
        # 从浏览器打开url网址
        browser.get(URL)
        # 显示等待定位搜索狂
        inputtxt = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#key')))  # 定位搜索框
        # 显示等待定位搜索按钮
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > div > div.form > button')))
        inputtxt.clear()
        inputtxt.send_keys(KEYWORD)
        button.click()
        time.sleep(1)
        for i in range(400):
            start = 30 * i
            end = 30 * (i + 1)
            browser.execute_script("window.scrollTo({},{})".format(start, end))
            time.sleep(0.001)
        # browser.execute_script("window.scrollTo(0,document.body.scrollHeght)")
        time.sleep(1)

        # 判断是否翻页成功
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList')))
        page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > em:nth-child(1) > b'))).text
        return page
    except TimeoutException as e:
        print(e)
        return get_search()


# 进入下一页
def next_page(page):
    if page == 1:
        get_info(browser.page_source)
    else:
        try:
            inputnum = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input')))
            button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a')))
            inputnum.clear()
            inputnum.send_keys(page)
            button.click()
            time.sleep(1)
            for i in range(400):
                start = 30 * i
                end = 30 * (i + 1)
                browser.execute_script("window.scrollTo({},{})".format(start, end))
                time.sleep(0.001)
            # browser.execute_script("window.scrollTo(0,document.body.scrollHeght)")
            time.sleep(1)

            # 判断是否翻页成功
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList')))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > a')))
            get_info(browser.page_source)
        except StaleElementReferenceException:
            next_page(page)
        except TimeoutException:
            next_page(page)


def get_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.select('#J_goodsList > ul > li')
    for data in lis:
        rs = {
            'url': data.select(" div > div.p-img > a")[0]['href'],
            # 'imgurl': data.select("div > div.p-img > a > img")[0]['src'],
            'price': data.select(".p-price i")[0].get_text(),
            'info': data.select(".p-name > a > em")[0].get_text().strip(),
            'commit': data.select(".p-commit > strong > a")[0].get_text().strip()[:-1],
            'shop': '京东自营' if len(data.select('.p-shop > span > a')) == 0 else data.select('.p-shop > span > a')[
                0].get_text()
        }
        save_data(rs)


def save_data(rs):
    if CONN.update_one({"url": rs['url']}, {'$set': rs}, True):
        print("保存成功" + str(rs))
    else:
        print("保存失败" + str(rs))


def main():
    page = get_search()
    # page = 5
    for i in range(1, int(page)):
        print("第{}页".format(i))
        next_page(i)


if __name__ == '__main__':
    client = pymongo.MongoClient('localhost')
    CONN = client[DB][COLLECTION]
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    main()
    client.close()  # 释放资源
    browser.close()
