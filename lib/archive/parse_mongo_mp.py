import requests
import re
# from bs4 import BeautifulSoup

from multiprocessing import Pool

import pandas  as pd
import pymongo
import random

import parser_config
import time

def get_parser_list():
    """Список парсеров"""
    method_list = [func for func in dir(parser_config) if callable(getattr(parser_config, func))]

    class_dict = {}
    for m in method_list:
        class_inst = getattr(parser_config, m)()
        if 'media' in dir(class_inst):
            media = class_inst.media

            class_dict[media] = class_inst

    return class_dict


def get_data(class_inst, href):
    """Получение данных"""
    x = class_inst.get_data(href)
    return x


def save_content(sp_db, to_insert):
    """"""
    insert_response = sp_db["text_total"].insert_one(to_insert)
    mg_id = insert_response.inserted_id
    #print(mg_id)

    return mg_id


def get_hrefs_queque(sp_db):
    """Получение ссылок в очереди"""
    # time.sleep(0.1)
    rgx = re.compile('(.+\/tag[s]*\/.+|kommersant\.ru\/gallery\/.+|.+rg\.ru\/author|im[0-9]\.kommersant\..+|\
kremlin\.ru\/catalog\/persons|\.ru\/photo|.+mailto.+|.+\.ru\/authors\/.+|vedomosti.ru/archive/|\
video|sujet|\/multimedia\/video|vedomosti\.ru\/comments|novayagazeta\.ru\/issues|\.jpg$|\
kommersant\.ru\/theme\/|rg\.ru\/tema|.+\.mp4+|.+\.mp4.+|visualrian|twitter|iz\.ru|interfax)')

    links_queque = sp_db["links_queque"].find({"$and": [{"status":'wait'},{"url":{'$not':rgx}}]}).skip(5000).limit(15000)

    # links_queque = sp_db["links_queque"].find({"$and": [{"status":'wait'},{"url_domain":"instagram.com"}]}).limit(50)

    #links_queque = sp_db["links_queque"].find({"$and": [{"status":'wait'}]}).limit(20000)
    #response = [v for v in links_queque]

    links_queque_list = [l for l in links_queque]
    return links_queque_list


def get_text(link):
    """Получение текста по ссылке"""
    sp_db = mongo_connect()

    x = {}
    link = {k:link[k] for k in link}
    link_href = link['url']
    try:
        domain = link['url_domain']
    except:
        domain = link['host']
    #domain = helper_html.get_domain(link_href)

    class_dict = get_parser_list()

    if domain in class_dict:

        parser_config = class_dict[domain]

        check = sp_db["text_total"].find_one({"url": link_href})

        if check is None:
            try:
                x = get_data(parser_config, link_href)
                x['media'] = domain

                if (x['title'] != 'not_set') & (x['fulltext'] != 'not_set'):
                    link["status"] = "saved"

                elif (x['title'] == 'not_set') & (x['fulltext'] != 'not_set'):
                    link["status"] = "saved"

                else:
                    link["status"] = "saved"

                sp_db["links_queque"].update( {"url" : link_href}, link)

                time.sleep(20)
                save_content(sp_db, x)

                print(link["status"], link_href)

            except Exception as e:
                link["status"] = "error"
                sp_db["links_queque"].update( {"url" : link_href},  link )
                print('Error', e)

        else:
            link["status"] = "saved_before"
            #print('Document Exist', link_href)
            # sp_db["links_queque"].update( {"url" : link_href},
            #     {"status" : status, "url" :link_href, "url_domain":domain} )

            print(link["status"], link_href)

    else:
        print('Domain not in list', link_href)

    return x

def mongo_connect():
    mgclient = pymongo.MongoClient("mongodb://localhost:27017/")
    sp_db = mgclient["semproxydb"]
    return sp_db


p = Pool(10)
if __name__ == '__main__':

    sp_db = mongo_connect()

    url_list = get_hrefs_queque(sp_db)
    random.shuffle(url_list)

    print('Начинаем чтение...')
    map_results = p.map(get_text, url_list)
    print('Готово')

    p.terminate()
