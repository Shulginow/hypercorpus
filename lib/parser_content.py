import sys
# sys.path.insert(0, '../lib')
sys.path.insert(0, '..')
sys.path.insert(0, '/home/v/vstoch2s/semproxy/Hyperco/')
import requests
import re
import pandas  as pd
import random
import parser_config
import time
import config
import datetime

from concurrent.futures import ThreadPoolExecutor


# from multiprocessing import Pool
from models import *
from bs4 import BeautifulSoup
from helper_html import HtmlProcess

helper_html = HtmlProcess()

def get_parser_list():
    """Список парсеров"""
    method_list = [func for func in dir(parser_config) if callable(getattr(parser_config, func))]
    class_dict = {}
    for m in method_list:
        class_inst = getattr(parser_config, m)()
        if 'media' in dir(class_inst):
            class_dict[class_inst.media] = class_inst

    return class_dict


def get_data(class_inst, href):
    """Получение данных"""
    x = class_inst.get_data(href)

    return x


def save_content(to_insert):
    """"""

    Content.insert(**to_insert).on_conflict('replace').execute()
    print('saved')
    return True


def get_hrefs_queque():
    """Получение ссылок в очереди"""

    include_pages = '[^>]+({})[^>]+'.format('|'.join(config.source_domains[-1:]))
    print(include_pages)
    filter_pages = config.filter_pages

    query= LinkQueque.select(LinkQueque.url, LinkQueque.url_domain).where(LinkQueque.status == 'wait')\
    .where(~LinkQueque.url.iregexp(filter_pages))\
    .where(LinkQueque.url.iregexp(include_pages))\
    .order_by(LinkQueque.id.desc()).limit(200).dicts()

    links_queque = [a for a in query]

    return links_queque


def update_queque(url, status='saved'):
    '''Обновление статуса в очереди'''

    query = LinkQueque.update(status=status).where(LinkQueque.url == url)
    query.execute()

    return True


def check_data(x):
    queque_status = 'saved'

    if len(x['text']) > 100:
        if  helper_html.is_anchor_link(x['hrefs']):
            queque_status= 'saved'
        else:
            queque_status='nonunchor_hrefs'
    else:
        queque_status='no_text'

    return queque_status


def get_text(link, sleep_time = 2):
    """Получение текста по ссылке"""
    x = {}

    domain = link['url_domain']
    url = link['url']

    class_dict = get_parser_list()

    if domain in class_dict:
        parser_config = class_dict[domain]

        print(url)

        check  = Content.select(Content.url).where(Content.url == url).first()
        print
        if check is None:
            print('Сохраняем')
            time.sleep(sleep_time)
            # try:

            x = get_data(parser_config, url)
            x['media'] = domain

            queque_status = check_data(x)

            if queque_status == 'saved':
                print('saved')
                save_content(x)

            # except Exception as e:
            #     queque_status = 'error'
            #     print('Error', e)

        else:
            print('Сохранено ранее')
            queque_status = "saved_before"

    else:
        queque_status = "error_domain_filter"
        print('Domain not in list', url)

    print(queque_status)
    update_queque(url, status=queque_status)

    return x

# def mongo_connect():
#     mgclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     sp_db = mgclient["semproxydb"]
#     return sp_db
# def run_mp():
#     url_list = get_hrefs_queque()
#     random.shuffle(url_list)
#     print(url_list)
#
#     print('Начинаем чтение...')
#     map_results = p.map(get_text, url_list)
#     print('Готово')
    # p.terminate()

def run_cf():
    concurrency = 5
    url_list = get_hrefs_queque()
    random.shuffle(url_list)
    print(url_list)

    with ThreadPoolExecutor(concurrency) as executor:
        for _ in executor.map(get_text, url_list):
            pass



    print('Готово')


def run_op():

    links = get_hrefs_queque()
    print(links)
    # for l in links:
    #     try:
    #         t = get_text(l)
    #     except Exception as e:
    #         print(e)


# p = Pool(processes=5)
if __name__ == '__main__':

    run_op()
    # run_cf()

    # dd = '2013-07-12T13:25:06+0400'
    # ddx = datetime.datetime.strptime(dd,'%Y-%m-%dT%H:%M:%S%z').date()
    # e = ['time', {'class': 'story__datetime'}, False, 'datetime']
    # sf = soup.find(*e[:2])
