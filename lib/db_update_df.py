import sys
sys.path.insert(0, '..')
import math
import numpy as np
import operator
import pandas  as pd
import re

# from __future__ import division, print_function
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk import word_tokenize, FreqDist
from helper_text import TxtParser
from helper_html import HtmlProcess
from models import *

helper_html = HtmlProcess()
helper_text = TxtParser()


def get_term_df(term):
    '''получение актуального df для конкретного слова'''

    # term_strict = '"{}"'.format(term)
    # df = sp_db.text_total.count_documents({'$text': {'$search': term_strict}})
    q = """
            SELECT COUNT(DISTINCT url_key) as links_count  FROM `content`
            WHERE MATCH (title_normalized,text_normalized) AGAINST ('{}')
            """.format(term)
    df = Content.raw(q)
    return df[0].links_count



def get_text_collection(skip, limit):
    '''получение сохраненных тектов'''
    data = Content.select(Content.text_normalized)\
    .where((~Content.text_normalized.is_null()) & (Content.text != 'not_set'))\
    .offset(skip).limit(limit).dicts()

    return data


def get_df_collection():
    '''получение слов с рассчитанным DF'''

    terms_total_dict= TermsDf.select(TermsDf.term).dicts()
    terms_total_dict = [h['term'] for h in terms_total_dict]

    return terms_total_dict


def update_term_df(term):
    '''обновление величины df в БД'''
    term_df = get_term_df(term)
    to_insert = {'term':term, 'df':term_df}
    # insert_response = sp_db["terms_df"].insert_one(to_insert)
    TermsDf.insert(**to_insert).on_conflict('replace').execute()
    return True


def insert_new_df(data, terms_total_dict):
    i = 0
    for doc in data:
        i+=1
        for term in word_tokenize(doc['text_normalized']):
            if term not in terms_total_dict:
                terms_total_dict.append(term)
                # check =  sp_db["terms_df"].find_one({"term": term})
                check  = TermsDf.select(TermsDf.term).where(TermsDf.term == term).first()

                if check is None:
                    update_term_df(term)
                    i+=1

    return terms_total_dict


def run_update():
    terms_total_dict  = get_df_collection()
    for term in terms_total_dict:
        update_term_df(term)

    return True


def run_insert():
    terms_total_dict  = get_df_collection()
    for i in range(50000, 150000, 1000):
        doc = get_text_collection(i, 1000)
        terms_total_dict = insert_new_df(doc, terms_total_dict)

        print(len(terms_total_dict),i)
    return True


if __name__ == '__main__':
    run_insert()

    # get_df('война')
