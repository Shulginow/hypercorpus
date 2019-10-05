import sys
sys.path.insert(0, '..')
sys.path.insert(0, '/home/v/vstoch2s/semproxy/Hyperco/')
import pandas  as pd
import re
import time
import config

from models import *
from bs4 import BeautifulSoup
from helper_html import HtmlProcess
helper_html = HtmlProcess()
##Исключаемые домены ссылок
stop_domains_re = ('|').join(list(map(re.escape,config.stop_domains)))
##Исключаемые классы
stop_elements_re = '.+'+('.+|.+').join(list(map(re.escape,config.stop_elements)))+'.+'
##Элементы ссылок которые надо удалить
link_part_remove = config.link_part_remove


CYCLE_COUNT = 200
SELECT_LIMIT = 40



def process_link(href, media):
    '''
    Обработка отдельной ссылки:
    добавление домена для внутренней ссылки
    удаление http
    '''

    l = helper_html.add_domain(href,media)
    l = helper_html.clean_http(l)
    l = re.sub(link_part_remove, '', l)
    l = l.strip().lower()

    return l


def check_transform_href(a_link, url, media):
    """
    Проверка ссылки для включения в список.
    Выделение источника ссылки и текста ссылки
    """

    response = False
    check = False

    if a_link.get('href') is not None:
        ##Проверка на элементы которые могут означать что ссылка нам не подходит
        if re.match(stop_elements_re, str(a_link)) is None:

            ##Удаление лишних элементов из ссылок
            href_clean = process_link(a_link.get('href'), media)
            text_clean = a_link.text.strip()

            if len(href_clean) > 1 and len(text_clean) > 0:
                if re.match(stop_domains_re, href_clean) is None:
                    check = True

    if check:
        response = {
            'source_url':href_clean,
            'link_text':text_clean,
            'document_url':helper_html.clean_http(url)
        }

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

        a_list = BeautifulSoup(element['hrefs']).find_all('a')

        for a_link in a_list:

            href_data = check_transform_href(a_link, element['url'],element['media'])

            if href_data:

                href_data['document_link_html'] = a_link
                href_data['link_sentense'] = helper_html.define_link_sentence(element['text'], a_link)
                href_data['document_domain'] = helper_html.get_host('http://{}'.format(href_data['document_url']))
                href_data['source_domain'] = helper_html.get_host('http://{}'.format(href_data['source_url']))

                href_list.append(href_data)

    except Exception as e:
        print(e)

    return href_list


def check_content(text):
    """Проверка текста - на то что это не просто сборник ссылок
        0:'too_many_links_in_text',
        1:'ok',
        2:'text_not_found',
        3:'links_not_found'
        4:'links_not_valid'
    """

    status = 0

    link_text = ' '.join(helper_html.define_links_text(text))
    total_text =  helper_html.clean_html(text)

    if len(link_text) < 2:
        status = 3

    if len(total_text) == 0:
        status = 2

    if status == 0:
        link_ratio = len(link_text) / len(total_text)
        if link_ratio < .5 and link_ratio > 0:
            status = 1

    return status


def set_content_status(url, status):

    print('Set status {} for url {}'.format(status, url))

    query = Content.update(status=status).where(Content.url_key == url)
    query.execute()
    return True


def get_content(select_limit):

    query= Content.select(Content.hrefs, Content.id, Content.url_key,
    Content.url, Content.text, Content.media).where(Content.hrefs != 'not_set')\
    .where(Content.status.not_in(['too_many_links_in_text','ok','text_not_found','links_not_found','links_not_valid']))\
    .where(Content.url_key.not_in(LinkStat.select(LinkStat.document_url)))\
    .limit(select_limit).dicts()

    return query


def get_link_info(content_rows):
    """Систематизация данных"""
    info_total = []
    stats =[]

    for element in content_rows:

        content_status = check_content(element['text'])

        if content_status == 1:

            element_parsed = parse_text(element)

            if  len(element_parsed)>0:
                info_total.extend(element_parsed)

            else:
                content_status = 4

        set_content_status(element['url_key'], config.text_status[content_status])

        if content_status == 1:
            save_data(info_total)
            # pass
        #stats.append([text_check, element['id']])
        # except Exception as e:
        #     print(e)
    return info_total


def save_data(data):
    for row in data:
        if row['source_domain'] in config.source_hosts:
            check  = LinkStat.select(LinkStat.id)\
            .where(LinkStat.link_sentense == row['link_sentense'])\
            .where(LinkStat.link_text == row['link_text']).first()

            if check is None:
                print('сохраняем данные в основную базу')
                # print(row)
                LinkStat.insert(**row).on_conflict('ignore').execute()
        else:
            check  = LinkStatOut.select(LinkStatOut.document_url)\
            .where(LinkStatOut.link_sentense == row['link_sentense'])\
            .where(LinkStatOut.link_text == row['link_text']).first()

            if check is None:
                print('сохраняем данные в дополнительную базу')
                LinkStatOut.insert(**row).on_conflict('ignore').execute()

    return 1


def run():
    for i in range(CYCLE_COUNT):
        print(i)
        content_rows = get_content(SELECT_LIMIT)
        info_total  = get_link_info(content_rows)


# def test_save():
#     row = {
#
#         'document_url': 'interfax.ru/world/628142',
#         'source_url': 'interfax.ru/world/612393',
#         'link_text': 'не просила',
#         'link_sentense':'''Пятилетний контракт В.Савельева истекает в октябре, он возглавляет "Аэрофлот" (MOEX: <a href="http://ifx.ru/Application/NewsBody.aspx#" rts="AFLT">AFLT</a>) более 9 лет.''',
#         'source_domain': 'interfax.ru',
#         'document_domain': 'interfax.ru',
#         'document_link_html': '''<a href="https://www.interfax.ru/world/612393" target="_blank"> не просила</a>'''
#     }
#
#     check  = LinkStatOut.select(LinkStatOut.document_url)\
#     .where(LinkStatOut.link_sentense == row['link_sentense'])\
#     .where(LinkStatOut.link_text == row['link_text']).first()
#     if check is None:
#         print('сохраняем данные в дополнительную базу')
#         LinkStatOut.insert(**row).on_conflict('ignore').execute()
#     else:
#         print('уже есть данные в бд', row['link_sentense'])




if __name__ == '__main__':
    run()
    # test_save()ѵ
