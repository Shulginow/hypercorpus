# import nltk
# nltk.download('stopwords')
# nltk.download('punkt')

import sys
sys.path.insert(0, '..')
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
stop_class_re = '.+'+('.+|.+').join(list(map(re.escape,config.stop_class)))+'.+'

CYCLE_COUNT = 2
SELECT_LIMIT = 4


ah = """
<a href="/doc/3739821?from=doc_vrez" target="_blank"><div class="photo"><img alt="Как власть помогает нефтяникам удерживать цены на нефть " class="lowsrc" src="https://im3.kommersant.ru/CorpImages/214у35.jpg"/><script>lowsrc()</script></div></a>
<a href="/doc/3739821" target="_blank">Как власть помогает нефтяникам удерживать цены на нефть </a>
"""


def process_link(href, media):
    '''
    Обработка отдельной ссылки:
    добавление домена для внутренней ссылки
    удаление http
    '''

    l = helper_html.add_domain(href,media)
    l = helper_html.clean_http(l)
    l = re.sub(config.link_part_replace, '', l)

    return l


def check_transform_href(a_link, url, media):
    """Проверка ссылки для включения в список"""

    response = False

    check = False
    if a_link.get('href') is not None:

        stop_class_match = re.match(stop_class_re,str(a_link))
        if stop_class_match is None:

            l = process_link(a_link.get('href'), media)

            if len(l) > 1:
                if re.match(stop_domains_re,l) is None:
                    t =  a_link.text
                    if len(t.strip())> 0:
                        check = True
    else:
        print('Отфильтовано по вхождению {}'.format(str(match)))

    if check:
        document_url = helper_html.clean_http(url)

        response = {
                        'source_url':l.strip().lower(),
                        'link_text':t.strip(),
                        'document_url':document_url
                    }
    return response


def test_check_transform_href():
    href_list = []
    a_list = BeautifulSoup(ah).find_all('a')
    for a_link in a_list:
        href_data = check_transform_href(a_link, 'url','media')
        if href_data:
            href_list.append(href_data)

    print(href_list)


def test_check_content():
    query= Content.select(Content.hrefs, Content.id, Content.url_key,
    Content.url, Content.text, Content.media).where(Content.url_key == 'kommersant.ru/doc/3758582').dicts()
    print(query[0]['text'])

    link_text = ' '.join(helper_html.define_links_text(query[0]['text']))
    print(link_text)


def test_search():
    q = 'снег'


    # query = Content.raw("""
    #         SELECT url_key, link_norm FROM content t1
    #         JOIN link_stat t2 on t1.url_key = t2.document_url
    #         WHERE MATCH (title_normalized,text_normalized) AGAINST ('{}')
    #         LIMIT 10""".format(q)).dicts()

    query = Content.raw("""
            SELECT link_norm, count(t2.id) count, avg(sim_stfidf5_link) sim_mean
            FROM content t1
            JOIN link_stat t2 on t1.url_key = t2.document_url
            WHERE MATCH (title_normalized,text_normalized) AGAINST ('{}')
            GROUP BY link_norm
            HAVING count > 1
            ORDER BY count DESC
            """.format(q)).dicts()


    # query= Content.select().where(Content.title_body.match(terms)).limit(20).dicts()
    print([(q['link_norm'], q['count']) for q in query])


if __name__ == '__main__':

    test_search()
