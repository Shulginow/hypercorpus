import sys
sys.path.insert(0, '..')

import gensim
import numpy  as np
import pandas as pd
import re
import time
# import warnings
# from bson.objectid import ObjectId
from models import *
from bs4 import BeautifulSoup
from helper_html import HtmlProcess
from helper_text import TxtParser
from helper_metrics import Metrics
from helper_vectors import Vectors

from nltk.tokenize import sent_tokenize
# from tqdm import tqdm


helper_text = TxtParser()
helper_html = HtmlProcess()
helper_metrics = Metrics()
helper_vectors = Vectors()

# w2v_model_path = '../models/ruscorpora_upos_skipgram_300_5_2018.vec.gz'
# w2v_model = gensim.models.KeyedVectors.load_word2vec_format(w2v_model_path)

def get_media_list():
    media_list = Content.select(Content.media).distinct()
    media_list = [i.media for i in media_list]
    return media_list


def get_data(row,media_dict):

    """Получение целевого текста и ссылки"""
    response = []
    rd = row.to_dict()

    domain = helper_html.get_domain(rd['source_url_original'])

    source_url_original = rd['source_url_original'].lower()

    if domain in media_dict:

        x = sp_db.text_total.find_one({"url":source_url_original})

        if x is None:
            print('Нет такого текста {}'.format(source_url_original))
        else:
            try:

                text_elements = [('source_title_norm', 'title_normalized'),
                                ('source_subtitle_norm', 'subtitle_normalized'),
                                ('source_text_norm', 'text_normalized')]
                for i in text_elements:
                    if i[1] in x:
                        rd[i[0]] = x[i[1]]
                    else:
                        rd[i[0]] = ''

                rd['source_text_elements_norm'] = '{} {} {}'.format(rd['source_title_norm'],
                                                                    rd['source_subtitle_norm'],
                                                                    rd['source_text_norm'])

                rd['source_text_elements_norm'] = rd['source_text_elements_norm'].strip()

                rd['source_text'] = x['fulltext']
                rd['source_title'] = x['title']

                response = rd
            except Exception as e:
                print(e)
    else:
        print("Домен не в списке СМИ", domain)

    return response

def text_pos_add(text):
    """добавление части речи к тексту - применение функции tag_ud"""
    text_tagged = [i for i in ud_model.tag_ud(text=text) if i in w2v_model.index2word]
    return text_tagged



def get_w2v_mean_similarity(t1, t2):
    """получение схожести двух массивов слов"""
    s_data = []
    for i in t1:
        for j in t2:
            try:
                s = w2v_model.wv.similarity(w1=i, w2=j)
                s_data.append(s)
            except:
                 pass

    r = np.array(s_data).mean()
    return r


def text_top_tfidf(text):
    """получение топа tf-idf из текста"""
    tid_list = metrics.get_text_tfidf(text)
    top_tfidf = [w[0] for w in tid_list[:10]]

    sum_tf_idf = sum([w[1] for w in tid_list[:10]])

    top_tfidf_str = ' '.join(top_tfidf)

    return top_tfidf, top_tfidf_str, sum_tf_idf


def domain_in_link(domain,link):
    """проверка вхождения домена в ссылку"""
    r = 0
    if domain in link:
        r = 1
    return r


def get_text_similarity(r):
    """
    получение схожести текстов по раличным методикам
    """

    try:

        link_text = BeautifulSoup(r.link_text).text
        r['link_norm'] = helper_text.text_normalise(link_text)

        link_article = BeautifulSoup(sp_db.text_total.find_one(ObjectId(r.raw_data_id))['text_normalized']).text
        link_text_tagged = text_pos_add(BeautifulSoup(link_article).text)


        to_tag = [r.source_title_norm, r.source_text_elements_norm, r.link_sentense, link_text, link_article]

        source_title_tagged, source_text_tagged, link_sentense_tagged, link_tagged, link_text_tagged = \
            [helper_vectors.text_pos_add(i) for i in to_tag]

        # source_title_tagged = [helper_vectors.text_pos_add(r.source_title_norm)]
        # #source_text_tagged = text_pos_add(r.source_text_norm)
        # source_text_tagged = helper_vectors.text_pos_add(r.source_text_elements_norm)
        # link_sentense_tagged = helper_vectors.text_pos_add(r.link_sentense)

        r['link_tagged']  = link_tagged

        r['document_url'] = helper_html.clean_http(r['document_url'])
        r['link_sentense'] = BeautifulSoup(r.link_sentense).text

        k = {
            'sim_stitle_link':[link_tagged, source_title_tagged],
            'sim_stext_link':[link_tagged, source_text_tagge],
            'sim_stext_lsentense':[link_tagged, source_text_tagged],
            'sim_stitle_lsentense':[link_sentense_tagged, source_title_tagged]
        }

        for i in k.items():
            r[i[0]] = helper_vectors.get_w2v_mean_similarity(*i[1])

        ##-----TF_IDF-----
        s_text_top_tid_list, s_text_top_tid_str, s_sum_tf_idf = text_top_tfidf(r.source_text_elements_norm)
        d_text_top_tid_list, d_text_top_tid_str, d_sum_tf_idf = text_top_tfidf(link_text)

        source_text_top_tid = text_pos_add(s_text_top_tid_str)
        document_text_top_tid = text_pos_add(d_text_top_tid_str)

        r['source_text_tfidf_top'] = ';'.join(s_text_top_tid_list[:5])
        r['document_text_tfidf_top'] = ';'.join(d_text_top_tid_list[:5])

         #Близость по топ 5 слов в текстах
        r['sim_stfidf_ltfidf'] = get_w2v_mean_similarity(text_pos_add(r['source_text_tfidf_top']),
                                                         text_pos_add(r['document_text_tfidf_top']))
        ##Близость топ-5 слова из целевого текста и текста ссылки
        #print(link_tagged, source_text_top_tid[:5])
        r['sim_stfidf5_link'] = get_w2v_mean_similarity(link_tagged, source_text_top_tid[:5])

        ##Близость топ-10 слова из целевого текста и текста ссылки
        r['sim_stfidf10_ltext'] = get_w2v_mean_similarity(link_tagged, source_text_top_tid[:10])

        ##Близость топ-5 слова из целевого текста и текста ссылки - каждый с каждым, максимальный
        #print(source_text_top_tid[:4])
        ms5 = get_max_similarity(link_tagged, source_text_top_tid[:5])

        if len(ms5) >0:
            ms5_pair = '/'.join(list(ms5[:2]))

            r['sim_stfidf5_link_max'] = ms5[2]
            r['sim_stfidf5_link_pair'] = ms5_pair
        else:
            r['sim_stfidf5_link_max'] = 0
            r['sim_stfidf5_link_pair'] = 0

    #         ##Близость топ-5 слова из целевого и исходного текста
    #         data_text.loc[i, 'sim_stfidf5_ltfidf5'] = get_w2v_mean_similarity(default_text_top_tid[:5],\
    #                                                                       source_text_top_tid[:5])

        ##Ссылка совпадает с доменом
        r['sim_domain_link']  = domain_in_link(r.source_domain,r.link_text)

        del r['source_url_original']

        ##Часть речи в ссылке
        ps = [x.split('_')[1] for x in link_tagged]
        for i in ps:
            r['link_ps_'+i] = 1


        ##конвертация
        r['_id'] = str(r['_id'])

        return r

    except Exception as e:
        print(e)
        return []

    return r


def check_link_text(row):
    response =True
#     print(row)
    for i in ['“Ъ” сообщал об этом', 'Ъ-Юг', 'Опубликован в разделе','Опубликован в разделах',
             'Читайте также']:
        if i in row.link_text:
            response=False
            break

    for i in ['Подробнее — в публикации “Ъ”', 'Опубликован в разделе','Опубликован в разделах']:
        if i in row.link_sentense:
            response=False
            break

    for i in ['XsltBlock']:
        if i in row.source_url_original:
            response=False
            break

    return response


def text_top_tfidf(text):
    """получение топа tf-idf из текста"""
    tid_list = metrics.get_text_tfidf(text)
    top_tfidf = [w[0] for w in tid_list[:10]]

    sum_tf_idf = sum([w[1] for w in tid_list[:10]])

    top_tfidf_str = ' '.join(top_tfidf)

    return top_tfidf, top_tfidf_str, sum_tf_idf


def domain_in_link(domain,link):
    """проверка вхождения домена в ссылку"""
    r = 0
    if domain in link:
        r = 1
    return r




def run():
    limit_num = 30

    for i in range(122400,180000, limit_num):

        x = sp_db.links_info.find().skip(i).limit(limit_num)

        links_info = pd.DataFrame([h for h in x])
        print(links_info.shape)

        for index, row in links_info.iterrows():
            if check_link_text(row):

                response = get_data(row,media_dict)

                if len(response) > 0:

                    if response['source_text'] !='not_set':

                        #print('Кол-во знаков:', len(response['source_text']))

                        data_text = pd.DataFrame([response])
                        result = get_text_similarity(data_text.loc[0])
                        time.sleep(0.1)

                        if len(result) > 0:

                            result = result.rename({'_id':'text_id', 'raw_data_id':'source_id'})

                            try:
                                to_insert = result.to_dict()
                                insert_response = sp_db["links_stat_3"].insert_one(to_insert)
                                print('Сохранено')
                            except Exception as e:
                                print(e)
    #             else:
    #                 print('Целевой текст не найден', row.source_url_original)

            else:
                print('Текст ссылки в исключениях', row.link_text)



def run():
    print(1)


if __name__ == '__main__':
    run()
