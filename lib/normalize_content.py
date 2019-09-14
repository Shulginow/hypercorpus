import sys
sys.path.insert(0, '..')
import time
import math
import numpy as np
import operator
import pandas  as pd
import pymongo
import re

from models import *
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize, FreqDist
from helper_text import TxtParser
from helper_html import HtmlProcess

helper_html = HtmlProcess()
helper_text = TxtParser()


def html_normalise(text):

    text = helper_text.clean_html(text)
    text_norm = helper_text.text_normalise(text,use_stop_words = True)
    return text_norm


def update_data(data):
    '''Обновление даных - добавление нормализованного текста'''
    for x in data:

        if 'text' in x:
            try:
                media=x['media']
            except:
                media = helper_html.get_domain(x['url'])

            update = {}
            for k in ['text', 'title', 'subtitle']:
                if k in x:
                    if k == 'text':
                        text = text_cut(x['text'], media)

                    update[k+'_normalized'] = html_normalise(x[k])
            print('Update', x['url'])
            update_content(x['url'], update)

        else:
            print(x)

    print('загружено')
    return 1


def update_content(cond, data):
    '''Обновление статуса в очереди'''
    query = Content.update(**data).where(Content.url == cond)
    query.execute()

    return True


def text_cut(text, media):
    '''Обрезка кусков текста в зависимости от СМИ'''
    if media == 'kremlin.ru':
        regexp_text = '<p>Опубликован в раздел(ах|е):\s*\n*\s*<a(.|\s)+'
        text = re.sub(regexp_text,'',text)

    return text


def run():
    for i in range(30):
        try:
            print(i)
            # (Content.hrefs != 'not_set') &
            query= Content.select()\
            .where(Content.text_normalized.is_null() & (Content.text != 'not_set'))\
            .limit(100).dicts()

            data = [h for h in query]

            print('{} rows selected'.format(len(data)))
            print(data[0])
            update_data(data)

        except Exception as e:
            print(e)



if __name__ == '__main__':
    run()
