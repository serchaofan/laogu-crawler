from multiprocessing import *
import requests
from bs4 import BeautifulSoup
from urllib import parse
import os
import sys
import time
from tkinter import filedialog, Tk


class DanbooruCrawler():
  def __init__(self):
    self.header = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }
    self.url_dict = {
      'danbooru': 'https://danbooru.donmai.us/posts?page={}&{}',
      'yandere': 'https://yande.re/post?page={}&{}',
      'konachan': 'http://konachan.com/post?page={}&{}'
    }
    print('''
    先去Danbooru/Yandere/Konachan查看要爬取的关键词，注意空格需要转为_，并查看能爬取的页数
    然后根据总页数决定要爬的页数
    关键词最好从搜索栏复制过来
    ''')

    url_choice = input('''
      1. Danbooru
      2. Yandere
      3. Konachan
      
      选择要爬取的网页（编号）：
    ''')
    while True:
      if url_choice == '1':
        self.web_name = 'danbooru'
        break
      elif url_choice == '2':
        self.web_name = 'yandere'
        break
      elif url_choice == '3':
        self.web_name = 'konachan'
        break
      else:
        print("输入错误重新输入")
    self.url = self.url_dict[self.web_name]

    self.data = {}
    self.data['tags'] = input("输入要找的关键词：")
    self.endpage = int(input("终止页:"))
    print("选择保存的目录")
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    self.pic_dir = filedialog.askdirectory()
    if not self.pic_dir:
      self.pic_dir = os.path.abspath(f".\\{self.data['tags']}")

    self.pic_name = input("图片名（后缀会统一用数字）：")

    self.page_urls = []
    self.images_urls = []

  def get_pages(self, url):
    sys.stdout.write("\r正在获取第{}/{}页".format(self.page_urls.index(url) + 1, self.endpage))
    html = requests.get(url, headers=self.header)
    html.encoding = "utf-8"
    soup = BeautifulSoup(html.text, 'html.parser')

    if self.web_name == "danbooru":
      articles = soup.find_all('article')
      for article in articles:
        data_file_url = article.get('data-file-url')
        self.images_urls.append(data_file_url)
    elif self.web_name == "yandere" or self.web_name == "konachan":
      articles = soup.find_all("a", class_="directlink largeimg")
      for article in articles:
        self.images_urls.append(article['href'])
    # print(self.images_urls)

  def get_images(self, image, count):
    suffix = "_{}.jpg".format(count)
    pic_abspath = '{}{}{}{}'.format(self.pic_dir, os.sep, self.pic_name, suffix)
    r = requests.get(image)
    with open(pic_abspath, 'wb') as f:
      f.write(r.content)
    sys.stdout.write("\r已下载{}%".format(round(count * 100 / len(self.images_urls), 1)))

  def start_crawling(self):
    if not os.path.exists(self.pic_dir):
      os.makedirs(self.pic_dir)

    data_str = parse.urlencode(self.data).replace(':', '%3A').replace('(', '%28').replace(')', '%29')

    # 生成页面列表
    for i in range(1, self.endpage + 1):
      self.page_urls.append(self.url.format(i, data_str))

    # 获取图片列表
    for url in self.page_urls:
      self.get_pages(url)

    print("\n图片url已获取完成，开始下载图片...")

    start_time = time.time()

    # 下载图片
    pool = Pool(processes=15)
    for image_url in self.images_urls:
      pool.apply_async(self.get_images, args=(image_url, self.images_urls.index(image_url) + 1))
    pool.close()
    pool.join()

    duration = time.time() - start_time

    print(f'''
    下载全部完成, 耗时：{int(duration / 60)}m, {int(duration % 60)}s
    ''')


if __name__ == '__main__':
  dc = DanbooruCrawler()
  dc.start_crawling()
