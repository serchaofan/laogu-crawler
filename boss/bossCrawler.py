from selenium import webdriver
from urllib import parse
from bs4 import BeautifulSoup
import lxml
import pandas as pd
import time
import json


class BossCrawler:
    def __init__(self):
        self.city_table = {
            'shanghai': 101020100,
            'suzhou': 101190400,
            'nanjing': 101190100,
            'hangzhou': 101210100,
            'wuxi': 101190200,
            'shenzhen': 101280600,
            'beijing': 101010100
        }
        self.job = ''
        self.city = ''
        self.page_num = 10
        self.url = ''
        self.company_list = []

    def get_pages(self):
        browser = webdriver.Chrome()
        browser.get(self.url)

        for i in range(self.page_num):
            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            comps = soup.find_all(class_="job-primary")

            for comp in comps:
                job_name = comp.find(
                    "span", attrs={"class": "job-name"}).find("a").get_text()
                job_area = comp.find(
                    "span", attrs={"class": "job-area"}).get_text()
                company_name = comp.find("div", attrs={
                    "class": "company-text"}).find("h3", attrs={"class": "name"}).get_text()
                job_salary = comp.find(
                    "div", attrs={"class": "job-limit"}).find("span").get_text()
                job_tag = list(set([i for i in comp.find(
                    "div", attrs={"class": "tags"})]))
                job_tag.remove('\n')
                job_tag = [i.get_text() for i in (job_tag)]
                company_welfare = comp.find(
                    "div", attrs={"class": "info-desc"}).get_text()
                company_info = comp.find("div", attrs={
                    "class": "company-text"}).find("p").get_text()

                self.company_list.append(json.loads(json.dumps(dict(公司名=company_name, 职业=job_name, 工作地=job_area,
                                                                    薪资=job_salary, 企业信息=company_info, 标签=job_tag, 福利=company_welfare))))

            time.sleep(1)
            browser.find_element_by_class_name("next").click()

        df = pd.json_normalize(self.company_list)
        with pd.ExcelWriter("out.xlsx") as writer:
            df.to_excel(writer, sheet_name=self.job)

    def start_crawling(self):
        begintime = time.time()
        self.job = input("请输入职业：")
        city_name = input("请输入城市(拼音)：")
        print(f"开始抓取BOSS直聘...")
        self.city = self.city_table[city_name]
        data = parse.urlencode(dict(query=self.job, city=self.city))
        self.url = f'https://www.zhipin.com/job_detail/?{data}'
        self.get_pages()
        print(f"抓取完成，耗时{round(time.time()-begintime)}s")


if __name__ == '__main__':
    bc = BossCrawler()
    bc.start_crawling()
