import sys
import pandas  as pd
import pymongo
import re
import time

from models import *
from bs4 import BeautifulSoup
from helper_html import HtmlProcess
helper_html = HtmlProcess()

##Исключаемые домены ссылок
stop_domains = ['telegram.me','vk.com','twitter.com/share',
                'javascript','id.vedomosti.ru',
                'zen.yandex.ru/iz','twitter.com/intent',
                'vk.com/app','tel:+','eepurl.com/cVRA-9',
               'facebook.com/sharer','connect.ok.ru/offer','//buy.vedomosti.ru','/sitemap/',
               '/search/']

stop_domains_re = ('|').join(list(map(re.escape,stop_domains)))

##Исключаемые классы
stop_class = ['float_href_block','get_news_link__bottom__yandex-zen','lowsrc',
              'Текстовая версия','cut__item cut__link','read_more',
              'data-vr-contentbox','b-incut__text','from=doc_vrez',
              'mailto:','rel="tag"','static\.kremlin\.ru'
             'print_link', 'h3','b-read-more__link','sitemap']


stop_class_re = '.+'+('.+|.+').join(list(map(re.escape,stop_class)))+'.+'

##Удаляем некоторые части из ссылок
link_part_replace = '(\?currentpage=main-country|mailto:.+|\?from=doc_vrez|www\.|\
                    |^#.*|http[s]*://|javascript.+|/$)'


def check_href(a_link, element_url, element_media):
    """Проверка ссылки для включения в список"""
    response = False
    match = re.match(stop_class_re,str(a_link))
    if match is None:
        a = a_link.get('href')
        t = a_link.text

        if a is not None:

            l = helper_html.add_domain(a, element_media)
            l = helper_html.clean_http(l)
            l = re.sub(link_part_replace, '', l)

            if len(l) > 1:
                if re.match(stop_domains_re,l) is None:
                    if len(t.strip())> 0:
                        response = [l.strip(),l.strip().lower(), t.strip(), element_url.strip().lower()]
    else:
        #print('Отфильтовано по вхождению {}'.format(str(match)))
        pass

    return response


def parse_text(element):
    """
    Получить ссылки из текста
    На вход: элемент из базы данных
    На выходе набор списков: для каждой ссылки адрес родительского документа,
    текст ссылки, адрес дочернего документа
    """

    href_list = []
    try:
        full_text = element['fulltext']
        element_url = element['url']
        element_media = element['media']

        soup = BeautifulSoup(element['hrefs'])
        a_list = soup.find_all('a')

        for a_link in a_list:
            href_text = helper_html.define_link_sentence(full_text, a_link)
            href_list_add = check_href(a_link, element_url,element_media)

            if href_list_add:
                href_list_add.append(href_text)
                href_list_add.append(a_link)
                href_list_add.append(element['_id'])

    #             href_list_add.append(text_tokenize_sentense(full_text))
                href_list.append(href_list_add)
    except Exception as e:
        print(e)

    return href_list


def get_link_info(hrefs):
    """Систематизация данных"""
    info_total = []
    stats =[]
    for element in hrefs:
        try:
            text_check = text_check_content(element['fulltext'])
            if text_check == 1:
                element_parsed = parse_text(element)
                info_total.extend(element_parsed)

            stats.append([text_check, element['_id']])
        except:
            pass

    return info_total,stats


def make_df(info_total):
    df = pd.DataFrame(info_total)
    df.columns = ['source_url_original','source_url','link_text','document_url',
                  'link_sentense','document_link_html','raw_data_id']
    df['document_domain'] = df.document_url.apply(helper_html.get_domain)
    df['source_domain'] = df.source_url.apply(helper_html.get_domain)

    df = df[df.link_sentense!=False]

    return df


def save_data(df, sp_db):
    """"сохранение стурктурированных данных по ссылка"""
    for index, row in df.iterrows():

        time.sleep(0.1)
        to_insert = {k:str(row.to_dict()[k])for k in row.to_dict()}

        check = sp_db.links_info.find_one({"source_url_original": to_insert['source_url_original'],
                                           'document_url':to_insert['document_url'],
                                           'link_text':to_insert['link_text'],
                                           'link_sentense':to_insert['link_sentense']})
        #print(check)
        if check is None:
            to_insert = {k:str(row.to_dict()[k])for k in row.to_dict()}
            insert_response = sp_db.links_info.insert_one(to_insert)
            print('загружено')
        else:
            pass
            #print('уже в базе')

    return 1
