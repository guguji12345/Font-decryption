import requests
from lxml import etree
from fontTools.ttLib import TTFont
import base64
import re


def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }
    session = requests.session()
    response = session.get(url,headers = headers)
    text = response.content.decode("gbk")
    html = etree.HTML(text)
    contents = html.xpath("//div[@class='tz-paragraph']//text()")

    url = re.findall(r"font-family.*?format\(.*?\).*?url\('(.*?)'\)",text)[0]
    url = "http:"+url
    font_ttf = session.get(url,headers=headers)
    text = font_ttf.content
    parse_file = 'car02.ttf'
    with open(parse_file,"wb")as f:
        f.write(text)

    result_dict = parse(parse_file)

    contentss = []
    for content in contents:
        for key in result_dict.keys():
            content = content.replace(key,result_dict[key])
        contentss.append(content)
    print(contentss)


def parse(parse_file):
    font_dict = [
        u'上', u'五', u'七', u'长', u'是', u'少', u'短', u'远', u'和', u'低', u'得', u'一', u'左',
        u'六', u'小', u'二', u'很', u'好', u'地', u'大', u'坏', u'下', u'高', u'右', u'多', u'的', u'着',
        u'不', u'矮', u'三', u'八', u'近', u'九', u'了', u'更', u'十', u'四', u'呢'
    ]

    font_base = TTFont("car01.ttf")
    font_base.saveXML("car01.xml")
    font_base_order = font_base.getGlyphOrder()[1:]

    font_parse = TTFont(parse_file)
    font_parse.saveXML("car02.xml")
    font_parse_order = font_parse.getGlyphOrder()[1:]

    font_base_flags = []
    for i in font_base_order:
        flags = font_base["glyf"][i].flags
        font_base_flags.append(flags)

    font_parse_flags = []
    for i in font_parse_order:
        flags = font_parse["glyf"][i].flags
        font_parse_flags.append(flags)

    result_dict = {}
    for a,i in enumerate(font_base_flags):
        for b,j in enumerate(font_parse_flags):
            if cmop(i,j):
                key = font_parse_order[b].replace("uni","")
                key = eval(r'u"\u'+str(key)+'"').lower()#eval()函数
                result_dict[key]=font_dict[a]
    print(result_dict)
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
    url = 'https://club.autohome.com.cn/bbs/thread/73ac39a287cc9678/69436529-1.html'
    get_data(url)
