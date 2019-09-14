import sys
sys.path.insert(0, '../lib')
sys.path.insert(0, '..')
sys.path.insert(0, '/home/v/vstoch2s/semproxy/Hyperco/')

import pandas  as pd
import re
import requests
import parser_config
import random
import time
import bs4
import config

# from tqdm import tqdm
from helper_html import HtmlProcess
from models import *

helper_html = HtmlProcess()

##Список доменов для добавления в базу
# source_lib = sp_db.text_parent_raw.find({"media": {"$regex": '.*'}}).distinct('media')


# ##Список исключений
# skip_pages = re.compile('(.+\/tag[s]*\/.+|kommersant\.ru\/gallery\/.+|.+rg\.ru\/author|im[0-9]\.kommersant\..+|\
# kremlin\.ru\/catalog\/persons|interfax\.ru\/photo|.+mailto.+|.+\.ru\/authors\/.+|vedomosti\.ru\/archive\/|\
# video|sujet|vedomosti\.ru\/comments/.+|ok\.ru)')

skip_url = re.compile('-----')

def get_parser_list():
    """Список парсеров"""
    method_list = [func for func in dir(parser_config) if callable(getattr(parser_config, func))]

    class_list = []
    for m in method_list:
        class_inst = getattr(parser_config, m)()
        if 'media' in dir(class_inst):
            media = class_inst.media
            class_list.append([class_inst, media])
    media_list = [m[1] for m in class_list]
    return class_list,media_list


def get_data_article(class_inst, href):
    """Получение данных классом parser_config"""
    x = class_inst.get_data(href)
    return x



def get_html(url, sess):
    """Получение кода HTML"""
    data = sess.get(url, headers=config.headers)
    data.connection.close()
    return data.text

def get_data(url, sess):
    """Получение объекта Beautiful Soup"""
    data = get_html(url, sess)
    soup=bs4.BeautifulSoup(data,'html.parser')
    return soup


# def get_request(url):
#     """Запроc данных с сайта"""
#     r = requests.get(url, timeout=10)
#     soup=bs4.BeautifulSoup(r.text, "html.parser")
#     return soup




def add_domain(a,host):
    """Добавление домена внутренним ссылкам"""

    a_domain = helper_html.get_domain(a)
    if a_domain is False and len(a) > 3 :
        a  = 'http://{}{}'.format(host,a)

    return a


def add_http(url, media):
    """Добавление http"""
    if re.match('^http',url) is None:
        if re.match('\/\w+',url):
            url = 'http://{}{}'.format(media,url)
        else:
            #print(url)
            url = False
            pass

    return url


def save_hrefs_queque(links, media, media_page, status = 'wait'):
    """Вставка ссылок в очередь"""

    response = []

    for url in links:
        save = True
        url = url.strip()

        url = add_http(url, media)

        if url:
            check  = LinkQueque.select(LinkQueque.url).where(LinkQueque.url == url).first()
            # check =  sp_db["links_queque"].find_one({"url": url})

            if check is None:

                url_domain = helper_html.get_domain(url)
                to_insert = {'url':url, 'url_domain':url_domain, 'source_domain':media,
                    'source':media_page, 'status':status}
                print(to_insert)
                LinkQueque.insert(**to_insert).on_conflict('replace').execute()
                # insert_response = sp_db.links_queque.insert_one(to_insert)
                # mg_id = insert_response.inserted_id
                # response.append(mg_id)

    return response


def queque_add_wait(url, source_lib):
    """Добавление ссылки в очередь"""

    sess = requests.Session()

    page_exclude = '(.+\.pdf|.+\.jpg|.+\.js|.+\.gif)'

    if re.match(page_exclude,url) is None:

        if re.match('^http',url) is not None:
            soup = get_data(url, sess)
            media = helper_html.get_domain(url)
            if media in source_lib:
                href_list_source_lib, href_list_all = get_hrefs(soup, media, source_lib)
                save_hrefs_queque(href_list_all, media, url)
            else:
                print('no_media in lib {}'.format(media))

        else:
            print('http')
    else:
        print('pdf/jpg')

    return 1


def get_candidates(skip_pages, source_lib):
    ''''''
    # .where(LinkQueque.url.iregexp(skip_pages))
    query= LinkQueque.select(LinkQueque.url).where(LinkQueque.status == 'wait')\
    .where(LinkQueque.url_domain << source_lib).order_by(LinkQueque.id.desc()).limit(1000).dicts()
    links = [a for a in query]

    rand_smpl = [links[i]['url'] for i in random.sample(range(len(links)), len(links))]
    links_index_pages = ['http://'+i for i in source_lib]
    links_index_pages.extend(rand_smpl)

    return links_index_pages


# class_list,media_list = get_parser_list()

def main():

    # source_lib = ['government.ru', 'sledcom.ru', 'mid.ru',
    #  'cbr.ru', 'gks.ru', 'kremlin.ru', 'interfax.ru', 'novayagazeta.ru',
    #  'rbc.ru',  'sport.rbc.ru', 'tass.ru', 'vedomosti.ru', 'tvrain.ru',
    #  'izvestia.ru','iz.ru',  'ria.ru']

    source_lib = ['pikabu.ru']

    skip_pages = '^((?!@|\/tag\/|\.ru\/images\/|author|im[0-9]\.|comments|\
    issues|video|sujet|multimedia|theme|\.ru\/photo).)*$'

    for i in range(100):
        print(i)
        links_index_pages =  get_candidates(skip_pages,source_lib)
        print(len(links_index_pages))

        for u in links_index_pages:
            print(u)
            try:
                queque_add_wait(u, source_lib)
            except Exception as e:
                print(u, e)


def get_hrefs(soup, host,source_lib):
    """Сбор всех ссылок со страницы"""

    href_list_source_lib = []
    href_list_all = []

    a_list = [str(a.get('href')) for a in soup.find_all('a')]
    a_list = list(set([re.split('#|\?', a)[0] for a in a_list]))

    r = []
    for a in a_list:

        a = add_domain(a,host)
        a_domain = helper_html.get_domain(a)
        href_list_all.append(a)
        if a_domain in source_lib:
            href_list_source_lib.append(a)


    return list(set(href_list_source_lib)), list(set(href_list_all))


# def test():
    # url = 'https://pikabu.ru/most-saved'
    # media = 'pikabu.ru'
    # source_lib = ['pikabu.ru']
    # sess = requests.Session()
    # soup = get_data(url, sess)
    # hrefs = get_hrefs(soup, media, source_lib)
    # href_list_source_lib, href_list_all = get_hrefs(soup, media, source_lib)
    # print(href_list_source_lib)
    # check  = LinkQueque.select(LinkQueque.url).where(LinkQueque.url == url).first()
    # if check is None:
    #     print(1)
    # else:
    #     print(2)


if __name__ == '__main__':
    main()
