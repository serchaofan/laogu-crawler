from bs4 import BeautifulSoup
from urllib import request, parse
import urllib
import requests
from lxml import etree
import os, sys
import time

print('''
先去Danbooru查看要爬取的关键词，注意空格需要转为_，并查看能爬取的页数
然后根据总页数决定要爬的页数
关键词最好从Danbooru的搜索栏复制过来
未使用多线程，爬取相当慢
''')

header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}
url = "https://danbooru.donmai.us/posts?page={}&{}"

str2 = {}
str2['tags'] = input("输入要找的关键词：")
endpage = int(input("终止页:"))
pic_dir = input("要存放的目录（末尾不加分隔符）: ")
pic_name = input("图片名（后缀会统一用数字）：")
str1 = parse.urlencode(str2).replace(':', '%3A').replace('(','%28').replace(')','%29')

images = []

for i in range(1, endpage+1):
    sys.stdout.write("\r正在获取第{}/{}页".format(i, endpage))
    articles = []
    finalurl = url.format(i, str1)
    html = requests.get(finalurl, headers=header)
    html.encoding = "utf-8"
    soup = BeautifulSoup(html.text, 'html.parser')
    articles = soup.find_all('article')
    for article in articles:
        data_file_url = article.get('data-file-url')
        images.append(data_file_url)
        
print("\n图片url已获取完成，开始下载图片...")

if not os.path.exists(pic_dir):
    os.makedirs(pic_dir)

count = 0
start_time = time.process_time()

for image in images:
    suffix = "_{}".format(count)
    pic_abspath = '{}{}{}{}'.format(pic_dir, os.sep, pic_name, suffix)
    r = requests.get(image)
    with open(pic_abspath, 'wb') as f:
        f.write(r.content)
    count = count + 1
    sys.stdout.write("\r已下载{}%".format(round(count*100/len(images), 1)))

duration = time.process_time() - start_time

print('''
下载全部完成，耗时{}s
'''.format(round(duration,2)))