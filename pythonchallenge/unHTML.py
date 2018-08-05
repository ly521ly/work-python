from html.parser import HTMLParser
from html.entities import name2codepoint
from urllib import request
import re
class MyHTMLParser(HTMLParser):
    def init(self):
        super(MyHTMLParser,self).init()
        self.__parsedata='' #设置一个空状态
def handle_starttag(self, tag, attrs):
    if ('class','event-title') in attrs:
        self.__parsedata='name' #设置爬取名称状态 
    if tag=='time':
        self.__parsedata='time'
    if ('class','say-no-more') in attrs:
        self.__parsedata='year'
    if ('class','event-location') in attrs:
        self.__parsedata='location'

def handle_endtag(self,tag):
    if tag == 'h3' or tag == 'span':
        self.__parsedata=''

def handle_data(self, data):
    if  self.__parsedata=='name':
        print('会议名称:%s'%data)

    if  self.__parsedata=='time':
        print('会议时间:%s'%data)

    if  self.__parsedata=='year':
        if re.match(r'\s\d{4}',data):
            #因为后面还有两组 say-no-more 后面的data却不是年份信息,所以用正则检测一下
            print('会议年份:%s'%data.strip()) 

    if  self.__parsedata=='location':
        print('会议地点:%s'%data)
        print('----------------------------------')
parser = MyHTMLParser()
URL = 'https://www.python.org/events/python-events/'
with request.urlopen(URL, timeout=1500) as f:  # 打开网页并取到数据
    data = f.read()
    parser.feed(data.decode('utf-8'))