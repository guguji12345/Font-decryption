from fontTools.ttLib import TTFont
import requests
import re
import time
from lxml import etree
import base64

def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }
    while True:
        session = requests.session()
        response = session.get(url,headers=headers)
        text = response.content.decode("utf-8")#lxml.html.document_fromstring可基本解码任意字符串
        html = etree.HTML(text)
        names = html.xpath("//dd[@class='w70 stonefont resumeName']/text()")#len=38
        sexs = html.xpath("//dd[@class='w48 stonefont']/text()")
        if names!=[]:
            break

    font_data_origin = re.search(r'base64,(.*?)\)', text, re.S).group(1)#找到的第一个
    font_data_after_decode = base64.b64decode(font_data_origin)

    font_parse = "font_parse.ttf"
    with open(font_parse, 'wb') as f:
        f.write(font_data_after_decode)

    result_dict = tff_parse(font_parse)

    namess = []
    sexss = []
    for name in names:
        for key in result_dict.keys():
            name = name.replace(key,result_dict[key])
            # if len(name)!=3:
            #     name = name.replace(str(name[:-2]),"刘")
        namess.append(name)
    print(namess)
    for sex in sexs:
        for key in result_dict.keys():
            sex = sex.replace(key,result_dict[key])
        sexss.append(sex)
    print(sexss)


def tff_parse(font_parse):#传入参数为文件名
    font_dict = [u'博', u'经', u'硕', u'届', u'大', u'刘', u'8', u'1', u'士', u'E', u'2', u'6', u'张',
                 u'M', u'验', u'5', u'本', u'赵', u'陈', u'吴', u'李', u'生', u'4', u'校', u'以', u'应', u'黄',
                 u'技', u'无', u'女', u'A', u'周', u'中', u'3', u'王', u'7', u'0', u'9', u'科', u'高', u'男',
                 u'杨', u'专', u'下', u'B'
    ]#len=45
    font_base = TTFont("font_base.ttf")#基础ttf从网页中下载,用于y用页面的打开的ttf进行判断
    font_base_order = font_base.getGlyphOrder()[1:]
    font_base.saveXML('font_base.xml')#调试用

    font_parse = TTFont(font_parse)#传入文件参数
    font_parse.saveXML('font_parse.xml')#调试用
    font_parse_order = font_parse.getGlyphOrder()[2:]


    f_base_flag = []#len=45
    for i in font_base_order:
        flags = font_base["glyf"][i].flags#字体对应的形状
        f_base_flag.append(list(flags))

    # print(len(f_base_flag))

    f_parse_flag = []#len=45
    for i in font_parse_order:
        flags = font_parse["glyf"][i].flags
        f_parse_flag.append(list(flags))
    # print(len(f_parse_flag))

    result_dict = {}
    for a,i in enumerate(f_base_flag):
        for b,j in enumerate(f_parse_flag):
            if comp(i,j):
                key = font_parse_order[b].replace("uni",'')
                key = eval(r'u"\u'+str(key)+'"').lower()#将所有字符转化为小写,转为16进制
                result_dict[key]=font_dict[a]
    print(result_dict)
    print(len(result_dict))
    return result_dict
#
def comp(i,j):
    if len(i)!=len(j):
        return 0
    for x in range(len(j)):
        if i[x] == j[x]:
            pass
        else:
            return 0
    return 1

if __name__ == '__main__':
    url = "https://su.58.com/qztech/"
    get_data(url)

