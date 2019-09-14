import os
import filters
import json
import plotly
import pandas as pd
import numpy as np
import operator
import process

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

MSQLDB.create_tables([LinkStat, LinkQueque], safe=True  )





# @app.route('/')
# def index():

    # select = {"status":{'$regex': 'wait'}, "host_page":{'$exists': True}}
    # links = mongo.db.links_queque.find(select).limit(10)
    #
    # text_urls = len(mongo.db.text_total.distinct('url'))
    # processed_urls = [i['document_url'] for i in mongo.db.links_stat_3.find({}, {'document_url':1,'_id':0})]
    # processed_urls_num = len(processed_urls)
    # processed_documents = len(list(set(processed_urls)))

    # return render_template("index.html",
    #     links=links, processed_urls=processed_urls_num, processed_documents=processed_documents,text_urls=text_urls)

# @app.route('/restore_data')
# def restore_data():
#     processed_links = LinkStat.select().dicts()
#     # processed_links = [i for i in processed_links if]
#     for pl in processed_links:
#         for i in ['sim_domain_link', 'sim_stext_link', 'sim_stext_lsentense',
#             'sim_stfidf10_ltext', 'sim_stfidf5_link', 'sim_stfidf5_link_max',
#             'sim_stfidf_ltfidf','sim_stitle_link', 'sim_stitle_lsentense']:
#             pl[i] = float(pl[i])
#         #return str(i)
#         insert_response = mongo.db.links_stat_3.insert_one(pl)
#
#     return str(pl)

@app.route('/move_data')
def move_data():
    processed_links = mongo.db.links_stat_3.find({})
    # processed_links = [i for i in processed_links if]

    data_df = pd.DataFrame([i for i in processed_links] )
    data_df = data_df.fillna(0)

    drop_names = ['raw_text_id','text_sim_w_tf_ifd', 'raw_text_if','source_text',
    'source_text_elements_norm','source_text_norm']

    for i in drop_names:
        if i in data_df.columns:
            data_df = data_df.drop([i], axis=1)

    data_df = data_df.drop_duplicates(subset=['document_url','source_url','link_text'])

    #processed_links = data_df.to_dict()
        #with MSQLDB.atomic():
            #LinkStat.insert_many(processed_links).on_conflict('replace').execute()

    for index, pl in data_df.iterrows():
        try:
            pl  = pl.to_dict()
            pl['link_norm_count'] = len(pl['link_norm'].split(' '))
            LinkStat.insert(**pl).on_conflict('replace').execute()

        except Exception as e:
            print(str(e))

    return str(pl)



# @app.route('/move_text')
# def move_text():
#     for n in range(0,200000, 100):
#         processed_links = mongo.db.text_total.find({}).skip(n).limit(100)
#         # processed_links = [i for i in processed_links if]
#
#         data_df = pd.DataFrame([i for i in processed_links] )
#         data_df = data_df.fillna('')
#         if 'rubrics' not in data_df.columns:
#             data_df['rubrics'] = 'not_set'
#         #data_df = data_df.drop_duplicates(subset=['document_url','source_url','link_text'])
#         #processed_links = data_df.to_dict()
#             #with MSQLDB.atomic():
#                 #LinkStat.insert_many(processed_links).on_conflict('replace').execute()
#         for index, pl in data_df.iterrows():
#
#             try:
#                 pl  = pl.to_dict()
#                 TextTotal.insert(**pl).on_conflict('replace').execute()
#
#             except Exception as e:
#                 print(str(e))
#
#     return str(pl)





def get_domain_count():

    ls= LinkStat.select(LinkStat.document_domain,fn.Count(LinkStat.id)\
    .alias('count')).group_by(LinkStat.document_domain)\
    .having(fn.Count(LinkStat.id) > 100).order_by(fn.Count(LinkStat.id).desc()).dicts()
    ls = [i for i in ls]

    x=[i['document_domain'] for i in ls]
    y=[i['count'] for i in ls]

    chart_data = {'x':x,'y':y, 'type':'bar'}
    chart_settings = {'title':'Количество сайтов со ссылками'}
    chart_url_count = process.make_chart(chart_data, chart_settings)
    return  chart_url_count


# def get_domain_pair_count():
#
#     ls= LinkStat.select(LinkStat.document_domain,LinkStat.source_domain,fn.Count(LinkStat.id)\
#     .alias('count')).group_by(LinkStat.document_domain, LinkStat.source_domain).dicts()
#     ls = [i for i in ls]
#
#     y=['{}-{}'.format(i['document_domain'], i['source_domain']) for i in ls]
#     x=[i['count'] for i in ls]
#
#     chart_data = {'x':x,'y':y, 'type':'bar', 'orientation':'h'}
#
#     chart_settings = {'title':'Количество пар сайтов со ссылками'}
#
#     chart_markup = process.make_chart(chart_data,chart_settings)
#
#     return  chart_markup


# def get_df():
#     df = mongo.db.terms_df.find({}).limit(100).sort('df', -1)
#     df = [i for i in df]
#     # return df
#     x = [i['df'] for i in df]
#     y = [i['term'] for i in df]
#
#     chart_data = {'x':x,'y':y, 'type':'bar', 'orientation':'h'}
#     chart_settings = {'title':'Топ DF','height':2000    }
#
#     chart_markup = process.make_chart(chart_data,chart_settings)
#
#     return  chart_markup

def get_link_word_count():

    ls= LinkStat.select(fn.COUNT(LinkStat._id).alias('word_count'),LinkStat.link_norm_count)\
    .where(LinkStat.link_norm_count < 10).group_by(LinkStat.link_norm_count).dicts()

    y=[i['word_count'] for i in ls]
    x=[i['link_norm_count'] for i in ls]

    chart_data = {'x':x,'y':y, 'type':'bar'}

    chart_settings = {'title':'Кол-во слов в ссылках'}

    chart_url_count = process.make_chart(chart_data, chart_settings)

    return  chart_url_count



def get_link_sim(pos_checked, count_checked, syntax_checked):

    features_list_pos = {
                    'pos_NOUN':LinkStat.link_ps_NOUN,
                    'pos_ADJ':LinkStat.link_ps_ADJ,
                    'pos_VERB':LinkStat.link_ps_VERB
                    }

    query= LinkStat.select(LinkStat.sim_stfidf5_link, fn.Count(LinkStat.id).alias('count'))
    #query_full_info = LinkStat.select()

    if 'pos_all' not in pos_checked:
        feature_cond = []
        for i in pos_checked:
            o = operator.eq(features_list_pos[i], 1)
            feature_cond.append(o)

        expr = reduce(operator.or_, feature_cond)
        query = query.where(expr)

        #query_full_info = query_full_info.where(expr)


    query = query.group_by(LinkStat.sim_stfidf5_link)

    if 'count_all' not in count_checked:
        feature_cond = []
        for c_che in count_checked:

            n = int(c_che.split('_')[1])
            if n > 3:
                feature_cond.extend([4,5,6,7,8,9,10])
            else:

                feature_cond.append(n)

        #expr = reduce(operator.and_, feature_cond)
        query = query.where(LinkStat.link_norm_count.in_(feature_cond))
        #query_full_info = query_full_info.where(LinkStat.link_norm_count.in_(feature_cond))

    root_dict = {'syntax_linkroot' :1, 'syntax_linknoroot' :0}
    if 'syntax_all' not in syntax_checked:

        feature_cond = []
        for s_che in syntax_checked:
            feature_cond.append(root_dict[s_che])

        query = query.where(LinkStat.link_is_root.in_(feature_cond))
    #full_info = query_full_info.limit(100)

    sim_count = [i for i in query.order_by(LinkStat.sim_stfidf5_link).dicts()]

    sim_count = pd.DataFrame(sim_count)
    sim_count.sim_stfidf5_link = sim_count.sim_stfidf5_link.apply(lambda x: round(float(x), 2))
    sim_count = sim_count.groupby('sim_stfidf5_link').sum().to_dict()


    x=[i[0] for i in sim_count['count'].items()]
    y=[i[1] for i in sim_count['count'].items()]

    chart_data = {'x':x,'y':y, 'type':'bar'}

    chart_settings = {'title':'Распределение по степени близости', 'height':300}
    chart = process.make_chart(chart_data, chart_settings)

    return  chart #full_info


def get_link_sim_word(word):
    '''Распределение по близости для одного слова'''

    query= LinkStat.select(LinkStat.link_norm, LinkStat.sim_stfidf5_link)\
    .where(LinkStat.link_norm == word).order_by(LinkStat.sim_stfidf5_link)

    sim_count = [i for i in query.dicts()]

    sim_count = pd.DataFrame(sim_count)
    sim_count.sim_stfidf5_link = sim_count.sim_stfidf5_link.apply(lambda x: round(float(x), 2))
    sim_count = sim_count.groupby('sim_stfidf5_link').count().to_dict()

    #return sim_count

    x=[i[0] for i in sim_count['link_norm'].items()]
    y=[i[1] for i in sim_count['link_norm'].items()]

    chart_data = {'x':x,'y':y, 'type':'bar'}

    chart_settings = {'title':'Распределение по степени близости', 'height':300}
    chart = process.make_chart(chart_data, chart_settings)

    return  chart #full_info



#full_info


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

    #chart_domain_count = get_domain_count()
    graphs = [
        get_domain_count(),
        process.get_link_pos(),
        get_link_word_count()
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

    #chart_domain_count = get_domain_count()
    graphs = [
        get_domain_count(),
        process.get_link_pos(),
        get_link_word_count()
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

    graphs  = [get_link_sim(pos_checked, count_checked, syntax_checked)]
    #return str(charts)

    ids = ['Диаграмма {}'.format(i+1) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)


    t = render_template('charts_link_sim.html',ids=ids,graphJSON=graphJSON,
        pos_options=pos_options, pos_checked=pos_checked, count_options=count_options,
        syntax_options=syntax_options,syntax_checked=syntax_checked,
        count_checked=count_checked)

    return t


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


@app.route('/text_by_phrase')
def text_by_phrase():
    """поиск текста по фразе"""
    try:
        phrase = request.args.get('ph', default = 'x')

        graphs = [
            get_link_sim_word(phrase)
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




if __name__ == '__main__':
    app.run()
