
import operator
import numpy as np
import pandas as pd

from peewee import *
from models import *
from functools import reduce



def get_domain_count():

    ls= LinkStat.select(LinkStat.document_domain,fn.Count(LinkStat.id)\
    .alias('count')).group_by(LinkStat.document_domain)\
    .having(fn.Count(LinkStat.id) > 100).order_by(fn.Count(LinkStat.id).desc()).dicts()
    ls = [i for i in ls]

    x=[i['document_domain'] for i in ls]
    y=[i['count'] for i in ls]

    chart_data = {'x':x,'y':y, 'type':'bar'}
    chart_settings = {'title':'Количество сайтов со ссылками'}
    chart_url_count = make_chart(chart_data, chart_settings)
    return  chart_url_count


def get_link_word_count():

    ls= LinkStat.select(fn.COUNT(LinkStat._id).alias('word_count'),LinkStat.link_norm_count)\
    .where(LinkStat.link_norm_count < 10).group_by(LinkStat.link_norm_count).dicts()

    y=[i['word_count'] for i in ls]
    x=[i['link_norm_count'] for i in ls]

    chart_data = {'x':x,'y':y, 'type':'bar'}

    chart_settings = {'title':'Кол-во слов в ссылках'}

    chart_url_count = make_chart(chart_data, chart_settings)

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
    chart = make_chart(chart_data, chart_settings)

    return  chart #full_info

def get_link_dist(word):
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
    chart = make_chart(chart_data, chart_settings)

    return  chart


def make_chart(chart_data, chart_settings):
    # , mode='markers'

    if 'x' in chart_data:
        chart_data = [chart_data]

    #l=dict(**chart_settings)

    chart = dict(
            data=chart_data,
            layout = chart_settings
        )
    return chart


def get_link_words_bubble(pos_checked, count_checked, syntax_checked):

    features_list_pos = {
                    'pos_NOUN':LinkStat.link_ps_NOUN,
                    'pos_ADJ':LinkStat.link_ps_ADJ,
                    'pos_VERB':LinkStat.link_ps_VERB
                    }

    query= LinkStat.select(LinkStat.link_norm, LinkStat.link_norm_count, fn.Count(LinkStat.id).alias('count'),
    fn.avg(LinkStat.sim_stfidf5_link).alias('sim_mean'),
    fn.avg(LinkStat.sim_stext_lsentense_w_tfifd).alias('sim_sentense_mean'))
    #query_full_info = LinkStat.select()

    if 'pos_all' not in pos_checked:
        feature_cond = []
        for i in pos_checked:
            o = operator.eq(features_list_pos[i], 1)
            feature_cond.append(o)

        expr = reduce(operator.or_, feature_cond)
        query = query.where(expr)

        #query_full_info = query_full_info.where(expr)

    query = query.group_by(LinkStat.link_norm, LinkStat.link_norm_count)

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


    root_dict = {'syntax_linkroot' :[1], 'syntax_linknoroot' :[0]}
    if 'syntax_all' not in syntax_checked:

        for s_che in syntax_checked:
            # field = s_che.split('_')[1]
            feature_cond = root_dict[s_che]
            query = query.where(LinkStat.link_is_root.in_(feature_cond))


    ls =  query.order_by(fn.Count(LinkStat.id).desc()).dicts()
    ls = [i for i in ls]

    ls_chart = ls[:1000]

    x=[i['sim_mean'] for i in ls_chart]
    y=[i['sim_sentense_mean'] for i in ls_chart]

    colors = []
    # for i in ls_chart:
    #     if i['link_norm_count'] == 1:
    #         colors.append('rgb(93, 164, 214)')
    #     if i['link_norm_count'] == 2:
    #         colors.append('rgb(255, 144, 14)')
    #     if i['link_norm_count'] == 3:
    #         colors.append('rgb(255, 144, 14)')
    #     else:
    #         colors.append('rgb(255, 65, 54)')


    if 'count_all' not in count_checked and  'pos_all' not in count_checked:
        size_del = 2
    elif 'count_all'  not in count_checked and  'pos_all' in count_checked:
        size_del = 6
    else:
        size_del = 4

    chart_data = [{ 'x':x,
                    'y':y,
                    'text': [i['link_norm'] + ' ' + str(i['count']) +' Близость текст-ссылка: \
                    '+ str(i['sim_mean']) for i in ls_chart],
                    'mode':'markers',
                    'name':'Кол-во слов',
                    'marker':{
                        'size': [np.log(i['count']) * 4 for i in ls_chart]
                        }
                    }
                ]






    chart_settings = {
                    'title':'Распределение близости',
                    'height':700,
                    'xaxis': {'title': 'Близость предложение-текст'},
                    'yaxis': {'title': 'Близость ссылка-текст'}
                 }

    chart_url_count = make_chart(chart_data, chart_settings)

    return  chart_url_count, ls


def get_search(q):

    ls = Content.raw("""
            SELECT link_norm, count(t2.id) count, avg(sim_stfidf5_link) sim_mean
            FROM content t1
            JOIN link_stat t2 on t1.url_key = t2.document_url
            WHERE MATCH (title_normalized,text_normalized) AGAINST ('{}')
            GROUP BY link_norm
            HAVING count > 1
            ORDER BY count DESC
            """.format(q))

    ls = [i for i in ls]

    return  ls


def get_linked(q):

    ls = Content.raw("""
            SELECT
                url_key,
                title,
                COUNT(DISTINCT document_url) as links_count,
                GROUP_CONCAT(DISTINCT(document_url) SEPARATOR '; ') input_documents,
                GROUP_CONCAT(link_norm SEPARATOR '; ') input_anchors
            FROM `content` t1
            INNER JOIN link_stat t2 on t2.source_url = t1.url_key
            WHERE url_key not like 'iz.ru' and MATCH (title_normalized,text_normalized) AGAINST ('{}')
            GROUP BY url_key
            HAVING links_count > 1
            ORDER BY links_count DESC
            """.format(q))

    # ls = [i for i in ls]
    content_list = []

    for i in ls :
        i.input_anchors =[x.strip() for x in i.input_anchors.split(';')]
        i.input_documents = [x.strip() for x in i.input_documents.split(';')]

        content_list.append(i)

    anchors_count = Content.raw("""
            SELECT
                t2.link_norm,
                COUNT(DISTINCT t2.document_url) as links_count
            FROM `content` t1
            INNER JOIN link_stat t2 on t2.source_url = t1.url_key
            WHERE url_key not like 'iz.ru' and MATCH (title_normalized,text_normalized) AGAINST ('{}')
            GROUP BY link_norm
            HAVING links_count > 1
            ORDER BY links_count DESC
            """.format(q))


    return  content_list, anchors_count


    # .from_(inner)

def get_link_words(pos_checked, count_checked, syntax_checked):

    features_list_pos = {
                    'pos_NOUN':LinkStat.link_ps_NOUN,
                    'pos_ADJ':LinkStat.link_ps_ADJ,
                    'pos_VERB':LinkStat.link_ps_VERB
                    }

    query= LinkStat.select(LinkStat.link_norm, fn.Count(LinkStat.id).alias('count'),
    fn.avg(LinkStat.sim_stfidf5_link).alias('sim_mean'))
    #query_full_info = LinkStat.select()

    if 'pos_all' not in pos_checked:
        feature_cond = []
        for i in pos_checked:
            o = operator.eq(features_list_pos[i], 1)
            feature_cond.append(o)

        expr = reduce(operator.or_, feature_cond)
        query = query.where(expr)

        #query_full_info = query_full_info.where(expr)

    query = query.group_by(LinkStat.link_norm)

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
            # field = s_che.split('_')[1]
            feature_cond.append(root_dict[s_che])

        query = query.where(LinkStat.link_is_root.in_(feature_cond))
        #query_full_info = query_full_info.where(LinkStat.link_norm_count.in_(feature_cond))


    # full_info = query_full_info.limit(1000)

    ls =  query.order_by(fn.Count(LinkStat.id).desc()).limit(1000).dicts()
    ls = [i for i in ls]

    ls_chart = ls[:100]

    x=[i['link_norm'] for i in ls_chart]
    y=[i['count'] for i in ls_chart]


    chart_data = [{'x':x,'y':y, 'type':'bar','name':'Кол-во слов'}]

    chart_data.append({'x':[i['link_norm'] for i in ls_chart],'y':[i['sim_mean'] for i in ls_chart],
    'type':'Scatter','yaxis':'y2', 'name':'Близость ср.', 'mode':'lines'})


    chart_settings = {'title':'Топ слов в ссылках',
        'height':300,
        'yaxis':{'title':''},
        'yaxis2':{
            'title':'',
            'overlaying':'y',
            'side':'right'
        }
    }
    chart_url_count = make_chart(chart_data, chart_settings)

    return  chart_url_count, ls


def get_link_paragraph():
    """Вхождение частей речи в ссылки"""

    data_report = LinkStat.select(
        LinkStat.sim_sp0_link_sentense,
        LinkStat.sim_sp1_link_sentense,
        LinkStat.sim_sp2_link_sentense,
        LinkStat.sim_sp3_link_sentense,
    ).where(((LinkStat.sim_sp4_link_sentense < 0.5) \
    | (LinkStat.sim_sp4_link_sentense > 0.6))&(LinkStat.sim_sp4_link_sentense > 0)).dicts()

    df = pd.DataFrame([i for i in data_report])
    dfm = df.melt()
    dfm.columns = ['paragraph', 'sim']

    r = {'sim_sp0_link_sentense':'Абзац 1',
        'sim_sp1_link_sentense':'Абзац 2',
        'sim_sp2_link_sentense':'Абзац 3',
        'sim_sp3_link_sentense':'Абзац 4',
    }

    dfm['paragraph'] = dfm['paragraph'].replace(r)
    dfm['sim'] = dfm['sim'].astype('float')

    chart_data = [
            {
                'type': 'violin',
                'x': dfm['paragraph'].values,
                'y': dfm['sim'].values,
                'points': 'none',
                'box': {
                'visible': True
            },
                'line': {
                    'color': 'green',
                },
                'meanline': {
                    'visible': True
                },
                'transforms': [{
                	 'type': 'groupby',
                     'groups': dfm['paragraph'].values,
                     'styles': [
                    	{'target': 'Абзац 1', 'value': {'line': {'color': 'blue'}}},
                    	{'target': 'Абзац 2', 'value': {'line': {'color': 'orange'}}},
                    	{'target': 'Абзац 3', 'value': {'line': {'color': 'green'}}},
                    	{'target': 'Абзац 4', 'value': {'line': {'color': 'red'}}}
                    ]
        	   }]
        }]

    # x1 = [float(i.sim_sp0_link_sentense) for i in data_report ]

    #
    # x2 = [i.sim_sp1_link_sentense for i in data_report]
    #
    # x3 = [i.sim_sp2_link_sentense for i in data_report]
    #
    # #x4 = [i.sim_sp3_link_sentense for i in data_report]
    #
    # colors = ['red', 'blue', 'green']
    #
    # dataset = [x1,x2,x3]
    #
    # chart_data = []
    #
    # for i in range(3):
    #
    #     trace = {
    #           'x': dataset[i],
    #           'type': "histogram",
    #           'opacity': 0.7,
    #           'marker': {
    #              'color': colors[i],
    #           }
    #         }
    #     chart_data.append(trace)
    #


    chart_settings = {
        'title':'Близость предложения ссылки к тексту',
        'yaxis': {
            'zeroline': False
          }
        }

    chart_url_count = make_chart(chart_data, chart_settings)

    return  chart_url_count



def get_link_pos():
    """Вхождение частей речи в ссылки"""
    ls= LinkStat.select(
        fn.SUM(LinkStat.link_ps_ADV).alias('link_ps_ADV'),
        fn.SUM(LinkStat.link_ps_NUM).alias('link_ps_NUM'),
        fn.SUM(LinkStat.link_ps_VERB).alias('link_ps_VERB'),
        fn.SUM(LinkStat.link_ps_NOUN).alias('link_ps_NOUN'),
        fn.SUM(LinkStat.link_ps_ADJ).alias('link_ps_ADJ'),
        fn.SUM(LinkStat.link_ps_INTJ).alias('link_ps_INTJ'),
        fn.SUM(LinkStat.link_ps_PROPN).alias('link_ps_PROPN')
    ).dicts()

    x=[i for i in ls[0]]
    y=[ls[0][i] for i in x]

    chart_data = [{'x':x,'y':y, 'type':'bar', 'name':'Кол-во вхождений'}]


    l_sim = LinkStat.select(
        LinkStat.link_ps_ADV,LinkStat.link_ps_NUM,
        LinkStat.link_ps_VERB,LinkStat.link_ps_NOUN,
        LinkStat.link_ps_ADJ,LinkStat.link_ps_INTJ,
        LinkStat.link_ps_INTJ, LinkStat.link_ps_PROPN,
        LinkStat.sim_stfidf5_link
    ).dicts()

    l_sim = pd.DataFrame([i for i  in l_sim])
    #colums_m = []
    colums_orig = ['link_ps_ADV', 'link_ps_NUM', 'link_ps_VERB', 'link_ps_NOUN', 'link_ps_ADJ', 'link_ps_INTJ',
           'link_ps_PROPN']

    for i in colums_orig:

        ik = i+'_m'
        l_sim[ik] = l_sim[i] * l_sim. sim_stfidf5_link
        l_sim[ik] = l_sim[ik].replace(0, np.nan)
        #colums_m.append(ik)

    l_sim.columns = [i[:-2] for i in l_sim.columns]
    l_sim_m = l_sim[colums_orig].mean().to_dict()


    chart_data.append({'x':[i[0] for i in l_sim_m.items()],
        'y':[i[1] for i in l_sim_m.items()],
        'type':'Scatter','yaxis':'y2', 'name':'Близость ср.', 'mode':'lines'})


    chart_settings = {'title':'Вхождение частей речи в ссылки',
        'yaxis':{'title':''},
        'yaxis2':{
            'title':'',
            'titlefont':{
                'color':'rgb(148, 103, 189)'
            },
            'tickfont':{
                'color':'rgb(148, 103, 189)'
            },
            'overlaying':'y',
            'side':'right'
        }
    }

    chart_url_count = make_chart(chart_data, chart_settings)

    return  chart_url_count
