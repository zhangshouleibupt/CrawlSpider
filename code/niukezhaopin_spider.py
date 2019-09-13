import requests
from bs4 import BeautifulSoup
import re
import jieba
import bs4
from tqdm import  tqdm
class BaseCrawlSpider():
    def get_all_url(self):
        raise NotImplementedError
    def parse_one_html_page(self,url,*args):
        raise NotImplementedError
    def get_all_job_detail_list(self):
        raise NotImplementedError
    #the common method that used in every class
    def get_one_html_page(self,url,encoding='utf8'):
        text = ''
        try:
            r = requests.get(url)
            r.raise_for_status()
            r.encoding = encoding
            text = r.text
        except:
            text = ''
        return text
class NowCoderWebCrawlSpider(BaseCrawlSpider):
    def __init__(self,root_url,base_url):
        self.root_url = root_url
        self.base_url = base_url
        self.name_list = ['岗位职责','岗位要求']
        super(NowCoderWebCrawlSpider,self).__init__()
    def get_all_url(self):
        all_url = []
        for i in range(1,7):
            this_url = self.base_url + str(i)
            text = self.get_one_html_page(this_url)
            soup = BeautifulSoup(text,'html.parser')
            all_a_tag = soup.find_all('a')
            for a_tag in all_a_tag:
                #class domain have many
                if 'reco-job-title' in a_tag.get('class',''):
                    url = a_tag.get('href','')
                    job_name = a_tag.string
                    all_url.append((job_name,url))
        all_url = [(job_name, self.root_url + url) for job_name,url in all_url if url]
        return all_url
    def parse_one_html_page(self,url,job_name):
        d = dict()
        text = self.get_one_html_page(url)
        soup = BeautifulSoup(text,'html.parser')
        d['job_name'] = job_name
        all_div_tag = soup.find_all('div')
        cnt = 0
        for div_tag in all_div_tag:
            if 'nc-post-content' in div_tag.get('class',''):
                children_tag = div_tag.children
                this_item_name = self.name_list[cnt]
                d[this_item_name] = [child.string for child in children_tag if child.string is not None]
                cnt += 1
        all_a_tag = soup.find_all('a')
        for a_tag in all_a_tag:
            if 'rec-com' in a_tag.get('class',''):
                h3 = a_tag.h3
                if isinstance(h3,bs4.element.Tag):
                    company_name = h3.string
                    d['company_name'] = company_name
        return d
    def get_all_job_detail_list(self):
        aLl_job_detail_list = []
        job_name_with_url_list = self.get_all_url()
        for job_name,url in tqdm(job_name_with_url_list):
            aLl_job_detail_list.append(self.parse_one_html_page(url,job_name))

    
nowcoder_root_url = 'https://www.nowcoder.com'
nowcoder_base_url = 'https://www.nowcoder.com/job/center?type=4&page='
nowcoder_spider = NowCoderWebCrawlSpider(nowcoder_root_url,
                                         nowcoder_base_url)
all_url_with_job_name = nowcoder_spider.get_all_job_detail_list()