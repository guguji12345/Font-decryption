import requests
from lxml import etree
from fontTools.ttLib import TTFont
import re
from selenium import webdriver
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
import time

def get_data():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches",["enable-automation"])
    browser = webdriver.Chrome(options=options)
    browser.get("https://www.douyu.com/topic/fans4615502")
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # element = WebDriverWait(browser,20).until(EC.presence_of_element_located((By.CLASS_NAME,'Title-followNum')))
    time.sleep(10)#加载页面
    # text= browser.execute_script("return document.documentElement.outerHTML")
    # html = browser.find_element_by_xpath("//*").get_attribute("outerHTML")# text = browser.page_source
    text = browser.page_source
    html = etree.HTML(text)
    url = re.findall(r'<div id="upsetFontStyle">.*?<style>.*?format\("woff"\).*?url\("(.*?)"\).*?format\("truetype"\).*?}.*?</style>',text,re.DOTALL)[0]#获取ttf文件
    url = "http:"+url
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }
    font_ttf = session.get(url,headers=headers)
    font_content = font_ttf.content
    parse_file = "斗鱼02.ttf"
    with open(parse_file,"wb")as f:
        f.write(font_content)

    result_dict = parse(parse_file)
    parse_dict = {"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9"}#基础键值对
    dict = {}#数字键值对
    for key1,value1 in result_dict.items():
        for key2,value2 in parse_dict.items():
            if key1 == key2:
                dict[value2]=value1
    # print(dict)#调试用
    all_num = []
    numbers = html.xpath("//span[@class='Title-followNum']/text()")[0]
    print(numbers)
    for number in numbers:
        if number in dict.keys():
            number = number.replace(number,dict[number])
            all_num.append(number)
    all_num = ''.join(all_num)
    print("该主播关注数为:%s"%all_num)


def parse(file):
    font_dict = [
        u'0',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9'
    ]#FontCreator打开01.ttf后的字符顺序

    font_base = TTFont("斗鱼01.ttf")#该文件为手动保存文件
    font_base.saveXML("斗鱼01.xml")
    font_base_order = font_base.getGlyphOrder()[1:]#第一个为无用数据

    font_parse = TTFont(file)
    font_parse.saveXML("斗鱼02.xml")
    font_parse_order = font_parse.getGlyphOrder()[1:]#同上
    print(font_parse_order)

    font_base_flags = []
    for i in font_base_order:
        flags = font_base["glyf"][i].flags#突出笔画痕迹
        font_base_flags.append(flags)

    font_parse_flags = []
    for i in font_parse_order:
        flags = font_parse["glyf"][i].flags#突出笔画痕迹
        font_parse_flags.append(flags)

    result_dict = {}
    for a, i in enumerate(font_base_flags):
        for b, j in enumerate(font_parse_flags):
            if cmop(i, j):#前置条件满足后,比较i,j是否相同
                key = font_parse_order[b]
                result_dict[key] = font_dict[a]
    print(result_dict)#调试用
    return result_dict

def cmop(i,j):
    if len(i)!=len(j):
        return 0
    for x in range(len(j)):
        if i[x]==j[x]:
            pass
        else:
            return 0
    return 1

if __name__ == '__main__':
    get_data()
    # parse("斗鱼01.ttf")#调试用