# -*- coding:utf-8 -*-

from xml.parsers.expat import ParserCreate
from urllib import request

class DefaultSaxHandler(object):
    weather = {'forecast': []}
    def start_element(self, name, attrs):
        if name == 'yweather:location':
            self.weather['city'] = attrs['city']
        elif name == 'yweather:forecast':
            self.weather['forecast'].append({
                    'date': attrs['date'],
                    'high': attrs['high'],
                    'low': attrs['low']
                })

def parseXml(xml_str):
    handler = DefaultSaxHandler()
    parser = ParserCreate()
    parser.StartElementHandler = handler.start_element
    parser.Parse(xml_str)
    return handler.weather

URL = 'https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20weather.forecast%20where%20woeid%20%3D%202151330&format=xml'

with request.urlopen(URL, timeout=4) as f:
    data = f.read()

result = parseXml(data.decode('utf-8'))
assert result['city'] == 'Beijing'