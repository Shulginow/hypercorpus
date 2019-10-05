import sys
sys.path.insert(0, 'lib')
sys.path.insert(0, '/home/v/vstoch2s/semproxy/Hyperco/lib')

import os
import filters
import json
import plotly
import pandas as pd
import numpy as np
import operator
import process
import parser_content

from peewee import *
from models import *
from functools import reduce
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
# from flask_pymongo import PyMongo


app = Flask(__name__)
@app.before_request
def _db_connect():
    MSQLDB.connect()

@app.teardown_request
def _db_close(exc):
    if not MSQLDB.is_closed():
        MSQLDB.close()

MSQLDB.create_tables([LinkStat, LinkStatOut, LinkQueque, Content, TermsDf], safe=True  )



@app.route('/', methods = ['POST', 'GET'])
def stat_links_index():

    pos_options, count_options, syntax_options = filters.get_filter_fields()

    if request.method == 'POST':
        f = request.form

        pos_checked = [i[0] for i in f.items() if 'pos' in i[0]]
        if len(pos_checked) == 0:
            pos_checked = ['pos_all']

        count_checked = [i[0] for i in f.items() if 'count' in i[0]]
        if len(count_checked) == 0:
            count_checked = ['count_all']

        syntax_checked = [i[0] for i in f.items() if 'syntax' in i[0]]
        if len(syntax_checked) == 0:
            syntax_checked = ['syntax_all']

        #return str(pos_checked)
    else:
        result = []
        pos_checked = ['pos_all']
        count_checked = ['count_all']
        syntax_checked = ['syntax_all']

    charts, phrase_data = process.get_link_words(pos_checked, count_checked, syntax_checked)

    graphs = [
        charts
    ]

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    t = render_template('charts_pos.html',ids=ids,graphJSON=graphJSON,
        pos_options=pos_options, pos_checked=pos_checked, count_options=count_options,
        syntax_options=syntax_options,syntax_checked=syntax_checked,
        count_checked=count_checked, phrase_data=phrase_data)

    return t


@app.route('/search', methods = ['POST', 'GET'])
def search():
    if request.method == 'GET':
        q = request.args.get('q')
        phrase_data = process.get_search(q)
        t = render_template('phrase_list.html', q = q, phrase_data=phrase_data)

        return t



@app.route('/linked', methods = ['POST', 'GET'])
def linked():
    if request.method == 'GET':

        try:
            q = request.args.get('q')
            content_list, anchors_count = process.get_linked(q)

            t = render_template('textlink_list.html', q = q, content_list=content_list, anchors_count=anchors_count)
        except Exception as e:
            t = str(e)
        return t




@app.route('/sim_words_count', methods = ['POST', 'GET'])
def sim_words_count():

    pos_options, count_options, syntax_options = filters.get_filter_fields()

    if request.method == 'POST':
        f = request.form

        pos_checked = [i[0] for i in f.items() if 'pos' in i[0]]
        if len(pos_checked) == 0:
            pos_checked = ['pos_all']

        count_checked = [i[0] for i in f.items() if 'count' in i[0]]
        if len(count_checked) == 0:
            count_checked = ['count_all']

        syntax_checked = [i[0] for i in f.items() if 'syntax' in i[0]]
        if len(syntax_checked) == 0:
            syntax_checked = ['syntax_all']

        #return str(pos_checked)
    else:
        result = []
        pos_checked = ['pos_all']
        count_checked = ['count_all']
        syntax_checked = ['syntax_all']


    charts, phrase_data = process.get_link_words_bubble(pos_checked, count_checked, syntax_checked)

    graphs = [
        charts
    ]

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    t = render_template('charts_pos.html',ids=ids,graphJSON=graphJSON,
        pos_options=pos_options, pos_checked=pos_checked,
        count_options=count_options, count_checked=count_checked,
        syntax_options=syntax_options,syntax_checked=syntax_checked,
        phrase_data=phrase_data)
    # return str([syntax_checked, syntax_options])
    return t


@app.route('/stat_docs')
def stat_docs():

    #chart_domain_count = process.get_domain_count()
    graphs = [
        process.get_domain_count(),
        process.get_link_pos(),
        process.get_link_word_count()
    ]
    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    t = render_template('charts_docs.html',ids=ids,graphJSON=graphJSON)

    return t

@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/stat_docs_1')
def stat_docs_1():

    #chart_domain_count = process.get_domain_count()
    graphs = [
        process.get_domain_count(),
        process.get_link_pos(),
        process.get_link_word_count()
    ]

    #return str(graphs[0]['data'])
    for ifile in range(len(graphs)):
        pd.DataFrame(graphs[ifile]['data'][0]).to_excel('x_{}.xlsx'.format(ifile))

    return str(1)

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    t = render_template('charts_docs.html',ids=ids,graphJSON=graphJSON)

    return t



@app.route('/stat_links_sim', methods = ['POST', 'GET'])
def stat_links_sim():

    pos_options, count_options, syntax_options = filters.get_filter_fields()

    if request.method == 'POST':
        f = request.form
        pos_checked = [i[0] for i in f.items() if 'pos' in i[0]]
        if len(pos_checked) == 0:
            pos_checked = ['pos_all']

        count_checked = [i[0] for i in f.items() if 'count' in i[0]]
        if len(count_checked) == 0:
            count_checked = ['count_all']

        syntax_checked = [i[0] for i in f.items() if 'syntax' in i[0]]
        if len(syntax_checked) == 0:
            syntax_checked = ['syntax_all']

        #return str(pos_checked)
    else:
        result = []
        pos_checked = ['pos_all']
        count_checked = ['count_all']
        syntax_checked = ['syntax_all']

    graphs  = [process.get_link_sim(pos_checked, count_checked, syntax_checked)]
    #return str(charts)

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)


    t = render_template('charts_link_sim.html',ids=ids,graphJSON=graphJSON,
        pos_options=pos_options, pos_checked=pos_checked, count_options=count_options,
        syntax_options=syntax_options,syntax_checked=syntax_checked,
        count_checked=count_checked)

    return t





@app.route('/text_by_phrase')
def text_by_phrase():
    """поиск текста по фразе"""
    try:
        phrase = request.args.get('ph', default = 'x')

        graphs = [
            process.get_link_dist(phrase)
        ]

        ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)


        data = LinkStat.select().where(LinkStat.link_norm == phrase)

        data_phrase = LinkStat.select(fn.Count(LinkStat.id).alias('count'),
            fn.avg(LinkStat.sim_stfidf5_link).alias('sim_mean'),
            fn.avg(LinkStat.sim_stext_lsentense_w_tfifd).alias('sim_sentense_mean'),
            fn.avg(LinkStat.sim_text_w_tfifd).alias('sim_text_mean'),).where(LinkStat.link_norm == phrase)

        data_total = LinkStat.select(fn.Count(LinkStat.id).alias('count'),
            fn.avg(LinkStat.sim_stfidf5_link).alias('sim_mean'),
            fn.avg(LinkStat.sim_stext_lsentense_w_tfifd).alias('sim_sentense_mean'),
            fn.avg(LinkStat.sim_text_w_tfifd).alias('sim_text_mean'),)

        data_diff ={
            'sim_diff':data_phrase[0].sim_mean - data_total[0].sim_mean,
            'sim_sentense_diff':data_phrase[0].sim_sentense_mean - data_total[0].sim_sentense_mean,
            'sim_text_diff':data_phrase[0].sim_text_mean - data_total[0].sim_text_mean,
            'sim_mean':data_total[0].sim_mean,
            'sim_sentense_mean':data_total[0].sim_sentense_mean,
            'sim_text_mean':data_total[0].sim_text_mean
        }
        #return str(data_diff)
        data = LinkStat.select().where(LinkStat.link_norm == phrase)

        data_count = len(data)

        return render_template('text_by_phrase.html',ids=ids,graphJSON=graphJSON,
        data=data, data_count=data_count, phrase=phrase, data_diff = data_diff,
        data_phrase = data_phrase)

    except Exception as e:
        return str(e)


@app.route('/stat_docs_paragraphs')
def stat_docs_paragraphs():

    #chart_domain_count = get_domain_count()
    graphs = [
        process.get_link_paragraph()
    ]

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]
    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    t = render_template('charts_docs.html',ids=ids,graphJSON=graphJSON)

    return t


@app.route('/text_detail/<id>')
def text_detail(id):
    """страница текста"""
    l = LinkStat.get(LinkStat._id == id)
    return render_template('text_detail.html',l=l)


def get_sim_corr(criterion = 'url'):
    '''Корреляция между близостью текста к тексту и ссылки к тексту'''

    c = {
        'url':LinkStat.document_domain,
        'w_count': LinkStat.link_norm_count
        }

    names = {
        'url':'СМИ',
        'w_count': 'Кол-во слов'
        }

    criterion_model = c[criterion]

    chart_data = []

    c_query = LinkStat.select(criterion_model.alias('cval'), fn.Count(LinkStat.id).alias('count')).\
    group_by(criterion_model).having(fn.Count(LinkStat.id) > 200).order_by(criterion_model)

    for criterion_value in c_query:#['zona.media', 'vedomosti.ru']:
        criterion_value = str(criterion_value.cval)

        query= LinkStat.select(LinkStat.sim_text_w_tfifd, LinkStat.sim_stfidf5_link)\
        .where(criterion_model == criterion_value).where(LinkStat.sim_stfidf5_link < 1)\
        .where(LinkStat.sim_text_w_tfifd > 0).where(LinkStat.sim_stfidf5_link > 0)

        if query is not None:

            x=[i.sim_text_w_tfifd for i in query]
            y=[i.sim_stfidf5_link for i in query]

            chart_data.append({'x':x,'y':y, 'type':'scatter', 'mode':'markers', 'name':criterion_value})

    chart_settings = {'title':'Распределение расстояния: {}'.format(names[criterion]), 'height':700,
        'xaxis': {'title': 'Близость текст-текст'},'yaxis': {'title': 'Близость ссылка-текст'}}


    chart = process.make_chart(chart_data, chart_settings)

    return  chart


def get_sim_s_corr(criterion = 'url'):
    '''Корреляция между близостью текста к предложению и ссылки к тексту'''

    c = {
        'url':LinkStat.document_domain,
        'w_count': LinkStat.link_norm_count,
        'link_is_root': LinkStat.link_is_root
        }

    names = {
        'url':'СМИ',
        'w_count': 'Кол-во слов',
        'link_is_root': 'Является корневым словом'
        }


    criterion_model = c[criterion]

    chart_data = []
    c_query = LinkStat.select(criterion_model.alias('cval'), fn.Count(LinkStat.id).alias('count')).\
    group_by(criterion_model).having(fn.Count(LinkStat.id) > 200).order_by(criterion_model)

    for criterion_value in c_query:#['zona.media', 'vedomosti.ru']:
        criterion_value = str(criterion_value.cval)

        query= LinkStat.select(LinkStat.sim_stext_lsentense_w_tfifd, LinkStat.sim_stfidf5_link)\
        .where(criterion_model == criterion_value).where(LinkStat.sim_stfidf5_link < 1)\
            .where(LinkStat.sim_stext_lsentense_w_tfifd > 0).where(LinkStat.sim_stfidf5_link > 0)

        if query is not None:

            x=[i.sim_stext_lsentense_w_tfifd for i in query]
            y=[i.sim_stfidf5_link for i in query]

            chart_data.append({'x':x,'y':y, 'type':'scatter', 'mode':'markers', 'name':criterion_value, 'opacity': 0.9})

    chart_settings = {'title':'Распределение расстояния: {}'.format(names[criterion]), 'height':700,
        'xaxis': {'title': 'Близость предложение-текст'},'yaxis': {'title': 'Близость ссылка-текст'}}


    chart = process.make_chart(chart_data, chart_settings)

    return  chart


@app.route('/sim_corr_1')
def sim_corr_1():
    """страница текста"""
    #return str(get_sim_corr())
    graphs = [
        get_sim_corr(criterion='url'),
        get_sim_corr(criterion='w_count')
    ]

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('charts_corr.html',ids=ids,graphJSON=graphJSON)


@app.route('/sim_corr_2')
def sim_corr_2():
    """страница текста"""
    try:
        graphs = [
            get_sim_s_corr(criterion='url'),
            get_sim_s_corr(criterion='w_count')
        ]

        ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('charts_corr.html',ids=ids,graphJSON=graphJSON)

    except Exception as e:
        return str(e)


@app.route('/sim_corr_p1')
def sim_corr_p1():
    """страница текста"""
    try:
        graphs = [
            get_sim_s_corr(criterion='url'),
            get_sim_s_corr(criterion='w_count')
        ]

        ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('charts_corr.html',ids=ids,graphJSON=graphJSON)

    except Exception as e:
        return str(e)



@app.route('/sim_corr_syn')
def sim_corr_syn():
    """страница текста"""
    try:
        graphs = [
            get_sim_s_corr(criterion='link_is_root'),
        ]

        ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('charts_corr.html',ids=ids,graphJSON=graphJSON)

    except Exception as e:
        return str(e)



@app.route('/check_page', methods = ['POST', 'GET'])
def check_page():
    url = 'https://habr.com/ru/post/186708/'
    host = 'habr.com'

    # url = 'https://www.rbc.ru/politics/12/09/2019/5d7a2d599a79472beb8896d5'
    # host = 'rbc.ru'


    r = parser_content.get_content_single(url, host)
    # t = render_template('check_page.html')
    return str(r)



if __name__ == '__main__':
    app.run()
