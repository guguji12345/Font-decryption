from fontTools.ttLib import TTFont
import requests
import re
import time
from lxml import etree
import base64
import pymongo

def get_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36"
    }

    session = requests.session()
    response = session.get(url,headers=headers)
    text = response.content.decode("utf-8")#lxml.html.document_fromstring可基本解码任意字符串
    html = etree.HTML(text)
    names = html.xpath("//ul[@class='canTouch']/li[1]/b/text()")
    day = html.xpath("//ul[@class='canTouch']/li[1]/em[1]/text()")
    box_offices = html.xpath("//ul[@class='canTouch']/li[@class='c2 ']//i/text()")
    total_boxs = html.xpath("//ul[@class='canTouch']/li[@class='c1']/em[2]/i/text()")
    box_office_ratios = html.xpath("//ul[@class='canTouch']/li[@class='c3 ']/i/text()")
    proportion_rows = html.xpath("//ul[@class='canTouch']/li[@class='c4 ']/i/text()")
    place_rates = html.xpath("//ul[@class='canTouch']/li[@class='c5 ']/span[1]/i/text()")

    font_data_origin = re.search(r'base64,(.*?)\)', text, re.S).group(1)#找到的第一个
    font_data_after_decode = base64.b64decode(font_data_origin)

    font_parse = "02.ttf"
    with open(font_parse, 'wb') as f:
        f.write(font_data_after_decode)

    result_dict = tff_parse(font_parse)

    boxs = []#实时票房
    totals = []#总票房
    ratioboxs = []#票房占比
    propors = []#排片占比
    placerate = []#上座率

    for box_office in box_offices:
        for key in result_dict.keys():
            box_office = box_office.replace(key,result_dict[key])
        boxs.append(box_office)

    for total in total_boxs:
        for key in result_dict.keys():
            total = total.replace(key,result_dict[key])
        totals.append(total)

    for ratio in box_office_ratios:
        for key in result_dict.keys():
            ratio = ratio.replace(key,result_dict[key])
        ratioboxs.append(ratio)

    for propor_row in proportion_rows:
        for key in result_dict.keys():
            propor_row = propor_row.replace(key,result_dict[key])
        propors.append(propor_row)

    for placing in place_rates:
        for key in result_dict.keys():
            placing = placing.replace(key,result_dict[key])
        placerate.append(placing)

    movies = list(zip(names,day,totals,boxs,ratioboxs,propors,placerate))
    all_movies = []
    for movie in movies:
        name,day,total,box,ratiobox,propor,placerate = movie
        all_movie = {
            "movie_name":name,
            "release_day":day,
            "total_box_office":total,
            "realtime_box":box,
            "box_office_ratio":ratiobox,
            "proportion_row":propor,
            "placing_rate":placerate
        }
        all_movies.append(all_movie)
    return all_movies

def mongo_storage(all_movies):
    client = pymongo.MongoClient(host="localhost",port=27017)
    db = client["maoyan_movie"]
    collection = db["movie_message"]
    for each_movie in all_movies:
        condition = {"movie_name":each_movie["movie_name"]}
        result = collection.find_one(condition)
        if result!=None:
            del result["_id"]
            if result != each_movie:
                collection.update_one(result,{"$set":each_movie})
            else:
                pass
        else:
            collection.insert_one(each_movie)


def tff_parse(font_parse):#传入参数为文件名
    font_dict = [u'1', u'7', u'8', u'2', u'6', u'4', u'0', u'9', u'5', u'3']#
    font_base = TTFont("01.ttf")#基础ttf从网页中下载,用于y用页面的打开的ttf进行判断
    font_base_order = font_base.getGlyphOrder()[2:]
    # font_base.saveXML('01.xml')#调试用

    font_parse = TTFont(font_parse)#传入文件参数
    # font_parse.saveXML('02.xml')#调试用
    font_parse_order = font_parse.getGlyphOrder()[2:]


    f_base_flag = []#len=45
    for i in font_base_order:
        flags = font_base["glyf"][i].flags#字体对应的形状
        f_base_flag.append(list(flags))

    f_parse_flag = []#len=45
    for i in font_parse_order:
        flags = font_parse["glyf"][i].flags
        f_parse_flag.append(list(flags))

    result_dict = {}
    for a,i in enumerate(f_base_flag):
        for b,j in enumerate(f_parse_flag):
            if comp(i,j):
                key = font_parse_order[b].replace("uni",'')
                key = eval(r'u"\u'+str(key)+'"').lower()#将所有字符转化为小写,转为16进制
                result_dict[key]=font_dict[a]
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
    url = "https://piaofang.maoyan.com/?ver=normal"
    all_movies = get_data(url)
    mongo_storage(all_movies)
