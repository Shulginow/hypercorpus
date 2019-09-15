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
# host_select = sp_db.text_parent_raw.find({"media": {"$regex": '.*'}}).distinct('media')


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

    a_domain = helper_html.get_host(a)
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
            if check is None:

                url_domain = helper_html.get_host(url)
                to_insert = {'url':url, 'url_domain':url_domain, 'source_domain':media,
                    'source':media_page, 'status':status}
                print(to_insert)
                LinkQueque.insert(**to_insert).on_conflict('replace').execute()
                # insert_response = sp_db.links_queque.insert_one(to_insert)
                # mg_id = insert_response.inserted_id
                # response.append(mg_id)

    return response


def queque_add_wait(url, host_select):
    """Поиск ссылок на странице и добавление их в очередь"""

    sess = requests.Session()

    page_exclude = '(.+\.pdf|.+\.jpg|.+\.js|.+\.gif)'

    if re.match(page_exclude,url) is None:

        if re.match('^http',url) is not None:
            soup = get_data(url, sess)
            url_host = helper_html.get_host(url)

            if helper_html.get_host(url) in host_select:

                href_list_host_select, href_list_all = get_hrefs(soup, url_host, host_select)
                save_hrefs_queque(href_list_all, url_host, url)

            else:
                print('no_media in lib {}'.format(url_host))

        else:
            print('http')
    else:
        print(page_exclude)

    return 1


def get_candidates(host_select, url_filter, offset_num):
    '''Получение кандидатов из очереди'''

    link_candidates = ['http://'+i for i in host_select]

    # .where(LinkQueque.url.iregexp(url_filter))
    query= LinkQueque.select(LinkQueque.url).where(LinkQueque.status == 'wait')\
    .where(LinkQueque.url_domain << host_select).order_by(LinkQueque.id.desc())\
    .offset(offset_num).limit(config.queque_limit).dicts()

    links = [a for a in query]
    rand_smpl = [links[i]['url'] for i in random.sample(range(len(links)), len(links))]
    link_candidates.extend(rand_smpl)

    return link_candidates


# class_list,media_list = get_parser_list()

def main():

    # host_select = ['government.ru', 'sledcom.ru', 'mid.ru',
    #  'cbr.ru', 'gks.ru', 'kremlin.ru', 'interfax.ru', 'novayagazeta.ru',
    #  'rbc.ru',  'sport.rbc.ru', 'tass.ru', 'vedomosti.ru', 'tvrain.ru',
    #  'izvestia.ru','iz.ru',  'ria.ru']

    host_select = ['habr.com']

    url_filter = '^((?!@|\/tag\/|\.ru\/images\/|author|im[0-9]\.|comments|\
    issues|video|sujet|multimedia|theme|search|\.ru\/photo).)*$'

    for offset_num in range(1,config.queque_limit*10, config.queque_limit):

        link_candidates =  get_candidates(host_select,url_filter,offset_num)

        for u in link_candidates:
            print(u)
            try:
                queque_add_wait(u, host_select)

            except Exception as e:
                print(u, e)


def get_hrefs(soup, host,host_select):
    """Сбор всех ссылок со страницы"""

    href_list_host_select = []
    href_list_all = []

    a_list = [str(a.get('href')) for a in soup.find_all('a')]
    a_list = list(set([re.split('#|\?', a)[0] for a in a_list]))

    r = []
    for a in a_list:

        a = add_domain(a,host)
        a_domain = helper_html.get_host(a)
        href_list_all.append(a)
        if a_domain in host_select:
            href_list_host_select.append(a)


    return list(set(href_list_host_select)), list(set(href_list_all))


# def test():
    # url = 'https://pikabu.ru/most-saved'
    # media = 'pikabu.ru'
    # host_select = ['pikabu.ru']
    # sess = requests.Session()
    # soup = get_data(url, sess)
    # hrefs = get_hrefs(soup, media, host_select)
    # href_list_host_select, href_list_all = get_hrefs(soup, media, host_select)
    # print(href_list_host_select)
    # check  = LinkQueque.select(LinkQueque.url).where(LinkQueque.url == url).first()
    # if check is None:
    #     print(1)
    # else:
    #     print(2)


if __name__ == '__main__':
    main()
