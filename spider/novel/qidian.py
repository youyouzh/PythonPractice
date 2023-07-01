#网站：https://book.qidian.com/
import random
import time
import requests
from lxml import etree
from requests.exceptions import RequestException

def get_response(url,headers,ciShu=1):  #get请求； ciShu为请求错误次数；错误控制台输出URL,可设置错误发起请求时间间隔
    i=1;text=None
    while i <= ciShu:
        i+=1
        try:
            respornse = requests.get(url=url, headers=headers)
            if respornse.status_code == 200:
                respornse.encoding = respornse.apparent_encoding
                text=respornse.text
                if text!=None:
                    break
            else:
                text=None
        except RequestException:
            text= None
        time.sleep(random.randrange(1,4))
    if text!=None:
        return text
    else:
        print(url)  # 输出请求失败的URL
        return None

def UserAgent():
    user_agent_list = ['Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36',
                   'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:17.0) Gecko/20100101 Firefox/17.0.6',
                   'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36',
                   'Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36']
    UserAgent={'User-Agent': random.choice(user_agent_list)}
    return UserAgent

def zhangJie_xpath(dict,lujing):#解析章节
    for title,href in dict.items():
        text=get_response(href,headers,ciShu=3)
        with open(lujing,'a',encoding='utf-8') as f:
            if text!=None:
                f.write(title+'\n')
                tre=etree.HTML(text)
                duanLuo_list=tre.xpath('//*[@class="read-content j_readContent"]/p')
                for duanluo_text in duanLuo_list:
                    duanluo=duanluo_text.xpath('./text()')[0]
                    f.write(duanluo+'\n')
            else:
                global rezhi
                rezhi[title]=href
        print(title,"下载成功")

def muLu_xpath(text):#解析目录
    dict={}#用于储存下载错误的连接
    tre=etree.HTML(text)
    zhangJie_list=tre.xpath('//*[@id="j-catalogWrap"]/div[2]/div')
    for zhangjie_text in zhangJie_list:
        zhangjie_list_1=zhangjie_text.xpath('./ul/li')
        for zhangjie_list_2 in zhangjie_list_1:
            href='https:'+zhangjie_list_2.xpath('./h2/a/@href')[0]
            title=zhangjie_list_2.xpath('./h2/a/text()')[0]
            dict[title]=href
    return dict

if __name__ == '__main__':
    rezhi={}
    url = 'https://book.qidian.com/info/1028150693/'
    lujing='E:\工作台\小说下载目录\诸天从斗罗开始的黄金圣衣 .txt'
    headers=UserAgent()
    text=get_response(url,headers)
    mulu_dict=muLu_xpath(text)
    zhangJie_xpath(mulu_dict,lujing)
    print(rezhi)