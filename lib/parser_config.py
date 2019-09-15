import sys
sys.path.insert(0, '..')
import re
import requests
import config
import json

# from fake_useragent import UserAgent
from bs4 import BeautifulSoup

class NewsParser:
    def __init__(self):
        pass

    def send_request(self, url):
        """Получение содержания"""


        if 'http' not in url:
            url = 'http://{}'.format(url)

        # headers = config.headers
        # headers['User-Agent'] = config.ua[3]
        sess = requests.Session()
        data = sess.get(url, headers=config.headers)
        data.connection.close()
        return data.text


    def read_content(self, soup, html_elements):
        """Чтение определенного тега, заданного в настройках"""
        tags_list = []

        try:
            for e in html_elements:
                data = soup.find(*e[:2])
                if data is not None:

                    if len(e) == 3:
                        txt = data.find_all(e[2])
                        txt = ' '.join(str(v) for v in txt)
                    elif len(e) == 4:
                        txt = soup.find(*e[:2]).get(e[3])
                    else:
                        try:
                            txt = data.text
                        except:
                            txt = ''
                    if len(txt):
                        tags_list.append(txt)

        except Exception as e:
            pass
                #print('не найден', str(e))
        response = ' '.join(tags_list)
        response = re.sub('\s+', ' ', response).strip()

        return response


    def read_html(self, url):
        '''Структурирование HTML-контента с обычных HTML страниц'''
        html = self.send_request(url)
        soup  = BeautifulSoup(html, "html5lib")
        ## Для всех ключей которые заданы в настроках парсера
        data_keys = [(k.strip('_'), v) for k, v in self.__dict__.items() if k not in ['media']]
        r = {'url':url}
        for i in  data_keys:
            #print(i[1])
            tag = self.read_content(soup, i[1])

            if len(tag) > 0:
                r[i[0]] = tag
            else:
                r[i[0]] = 'not_set'
        return r


    def read_instagram(self,url):
        '''Структурирование контента с Инстаграма'''
        r = {'url':url, 'media':self.media, 'title':'post'}
        try:
            html = self.send_request(url)
            soup = BeautifulSoup(html, 'html5lib')
            body = soup.find('body')
            script_tag = body.find('script')
            raw_string = script_tag.text.strip().replace('window._sharedData =', '').replace(';', '')
            json_data = json.loads(raw_string)

            text = json_data['entry_data']['PostPage'][0]['graphql']\
                ['shortcode_media']['edge_media_to_caption']['edges'][0]['node']['text']

            author = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username']

            r['text'] = text
            r['author'] = author

        except:
            r['text'] = 'not_set'

        return r




    def get_data(self, url):
        """Объединяющая функция"""

        if re.match(r'.+\.pdf$', url):
            print('PDF', url)
            r = {'media':self.media, 'url':url, 'title':'pdf'}

        else:
            if self.media not in ['instagram.com']:
                r = self.read_html(url)
            else:
                print('Читаем инсту', url)
                r = self.read_instagram(url)

        return r

'''
Настройкми парсера под каждое СМИ
Порядок элементов:
0 - Элемент блока
1 - Атрибуты элемента блока
2 - Элементы внутри блока которые надо выбрать
3 - Если надо взять значение у атрибута

'''
class Rbc(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'rbc.ru'
        self.title = [['div',{'class':'article__header__title'}, 'span']]
        self.subtitle = [['div',{'class':'article__text__overview'}]]
        self.articledate = [['span',{'class':'article__header__date'}]]
        self.text =  [['div', {'class': 'article__text'}, 'p']]
        self.hrefs = [['div', {'class': 'article__text'}, 'a']]
        self.author = [['div',{'class':'article__authors'}]]
        self.tags = [['span',{'class':'article__tags__block'}]]


class Rbcmoney(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'money.rbc.ru'
        self.title = [['div',{'class':'article__header__title'}, 'span']]
        self.subtitle = [['div',{'class':'article__text__overview'}]]
        self.articledate = [['span',{'class':'article__header__date'}]]
        self.text =  [['div', {'class': 'article__text'}, 'p']]
        self.hrefs = [['div', {'class': 'article__text'}, 'a']]
        self.author = [['div',{'class':'article__authors'}]]
        self.tags = [['span',{'class':'article__tags__block'}]]


class Tass(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'tass.ru'
        self.hrefs = [['div', {'class': 'article__text'}, 'a'],['div',{'class':'text-content'},'a']]
        self.text =  [['div', {'class': 'article__text'}, 'p'], ['div',{'class':'text-content'},'p'],
        ['div',{'class':'text-content'},'h2']]
        self.subtitle = [['p',{'class':'article__lead'}], ['div',{'class':'news-header__lead'}]]
        self.articledate = [['dateformat',{},'span']]
        self.title = [['h1',{'class':'news-header__title'}],['div', {'class': 'publication__title'}]]
        self.author = []
        self.tags = [['div',{'class':'tags__list'},'a']]


class Ria(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'ria.ru'
        self.hrefs = [['div', {'class': 'b-longread__row'}, 'a'],
                    ['div',{'class':'b-article__ind'}, 'a']]
        self.text =  [
                            ['div',{'class':'b-article__ind'}, 'p'],
                            ['div',{'class':'b-article__ind'}, 'h3'],
                            ['div',{'class':'b-article__body'},'p'],
                            ['div',{'class':'b-article__body'},'h2'],

                            ['div', {'class': 'b-longread__row'}, 'p'],
                            ['h3', {'class': 'm-header'}]
                        ],
        self.articledate = [['div',{'class':'b-article__info-date'},'span']]

        self.subtitle = [['div', {'class': ' m-input_subtitle_article'},'span']]
        self.title = [
                    ['h1', {'class': 'b-article__title'},'span'],
                    ['div', {'class': 'm-input_title_article'},'span']
                    ],

        self.author = [['div', {'class': 'm-input_author'},'span']]
        self.tags = [['li',{'class':'b-article__tags-item'},'span']]


class Interfax(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'interfax.ru'
        self.hrefs = [['div', {'itemprop': 'articleBody'}, 'a']]
        self.text = [
                            ['article', {'itemprop': 'articleBody'}, 'p'],
                            ['div', {'itemprop': 'articleBody'}, 'p']
                        ]
        self.articledate = [['a', {'class': 'time'}]]
        self.title = [['h1', {'class': 'textMTitle'}]]
        self.subtitle = [['p',{'itemprop':'description'}]]
        self.author = [['div', {'itemprop':'author'}]]
        self.tags = [['div',{'class':'textMTags'}, 'a']]


class Kommersant(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'kommersant.ru'
        self.hrefs = [
                ['p', {'class': 'b-article__text'}, 'a'],
                ['div', {'class': 'article_text_wrapper'}, 'a']
            ]
        self.text =  [
                ['div', {'class': 'article_text_wrapper'}, 'p'],
                ['div', {'class':"article_text_wrapper"}, 'font']
            ]

        self.articledate = [
                ['time', {'class': 'b-article__publish_date'}],
                ['time', {'itemprop': 'datePublished'}]
            ]
        self.title = [
                ['h2', {'itemprop': 'alternativeHeadline'}], ['h1', {'class': 'article_name'}],
                ['p', {'class':"b-article__text"}, 'font']
            ]
        # ['h4', {'class': 'article_name'}]
        self.subtitle = [
                ['h1', {'class': 'article_subheader'}]
            ]

        self.author = [
                ['p', {'class': 'document_authors'}]
            ]

        self.tags = []


class Vedomosti(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'vedomosti.ru'
        # self.hrefs = [['div', {'class': 'b-document__body'}, 'a']]
        self.hrefs = [['article', {}, 'a']]
        self.text =  [['div', {'class': 'b-document__body'}, 'p'],
            ['div',{'class':'b-news-item__text_one'},'p'],
            ['div',{'class':'description'}]
        ]
        self.articledate = [['time', {'class': 'b-article__publish_date'}],
        ['time', {'itemprop': 'datePublished'}],
        ['span', {'class':'b-published_at_time'}]]
        self.title = [['h1', {'class': 'title'}], ['div',{'class':'b-news-item__title_one'},'h1']]
        self.subtitle = [['div',{'class':'subtitle'}]]
        self.author = [['div', {'class': 'b-document__authors'}]]
        self.tags = []


class Kremlin(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'kremlin.ru'
        self.hrefs = [['div', {'class': 'read__internal_content'}, 'a']]
        self.text =  [['div', {'class': 'read__internal_content'}, 'p']]
        self.articledate = [['time', {'class': 'read__published'}]]
        self.title = [['h1', {'itemprop': 'name'}]]
        self.author = []
        self.tags = [['a', {'rel': 'tag'}]]


class Cbr(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'cbr.ru'
        self.hrefs = [['div', {'id': 'content'}, 'a']]
        self.text =  [['div', {'id': 'content'}, 'p']]
        self.articledate = [['div', {'class': 'separate_block'}, 'em'], ['em']]
        self.title = [['h3'], ['h1']]
        self.author = []
        self.tags = [['a', {'rel': 'tag'}]]


class Forbes(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'forbes.ru'
        self.hrefs = [['div', {'class': 'all-body'}, 'a']]
        self.text =  [
            ['div', {'class': 'all-body'}, 'p'],
            ['div',{'class':'facts-profile-content'},'p'],
            ['div',{'class':'personal-data'},'div']
        ]
        self.articledate = [['span', {'class': 'date'}]]
        self.title = [['h1',{'class':'title'}], ['h1']]
        self.subtitle = [['div',{'class':'subtitle'}]]
        self.author = [['div', {'class': 'author-material'}]]
        self.tags = [['div', {'class': 'block-hashtag'}, 'a']]


class Government(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'government.ru'
        self.hrefs = [['div', {'class': 'all-body'}, 'a']]
        self.text =  [
            ['div', {'class': 'reader_article_body'}],
            ['div', {'class': 'reader_article_lead'}]
            ]
        self.articledate = [['span', {'class': 'reader_article_dateline__date'}]]
        self.title = [['h3',{'class':'reader_article_headline'}], ['h1']]
        self.subtitle = []
        self.author = []
        self.tags = [['div', {'class': 'reader_article_meta'}, 'a']]


class Oneonetwoo_ua(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = '112.ua'
        self.title = [['h1',{'class':'h1'}],['h1',{'class':'title-pl-list'}],
        ['div', {'class':'b-center-item-head-info'},'h1']]
        self.subtitle = [['p',{'class':'top-text'}]]
        self.text =  [['div', {'class': 'article-content_text'}],
            ['section',{'class':'page-cont'}], ['div', {'class':'article-text'}, 'p']]
        self.hrefs = [['div', {'class': 'article-content_text'}, 'a'],
            ['section',{'class':'page-cont'},'a']]
        self.articledate = [['span', {'class': 'datetime'}],
            ['div', {'class': 'time'}]]
        self.author = [['h3',{'class':'list-title'}]]
        self.tags = [['div', {'class': 'article-tags'}, 'a']]


class Sledcom(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'sledcom.ru'
        self.title = [['div',{'class':'news-card__title-text'}],
        ['div',{'class':'cd-title'},'h2']]
        self.subtitle = [['p',{'class':'top-text'}]]
        self.articledate = [['div', {'class': 'news-card__data'}],
        ['div',{'class':'bn-date'}]]
        self.text =  [['div', {'class': 'news-card__text'}],
        ['article',{},'p']]
        self.hrefs = [['div', {'class': 'news-card__text'}, 'a']]
        self.author = [['h3',{'class':'list-title'}]]
        self.tags = [['div', {'class': 'news-card__tags'}, 'a']]


class Mid(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'mid.ru'
        self.title = [['h1']]
        self.subtitle = []
        self.articledate = [['span', {'class': 'article-status-line'}]]
        self.text =  [['article', {'class': 'article'}]]
        self.hrefs = [['article', {'class': 'article'}, 'a']]
        self.author = []
        self.tags = []


class Rg(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'rg.ru'
        self.title = [['h1',{'class':'b-material-head__title'}],
            ['h2',{'class':'article-main__heading__item'}]]
        self.subtitle = []
        self.articledate = [['span', {'class': 'b-material-head__date-day'}],
            ['span', {'class': 'article-main__meta__item_date'}]]


        self.text =  [['div', {'class': 'b-material-wrapper__text'}]]
        self.hrefs = [['div', {'class': 'b-material-wrapper__text'},'a']]
        self.author = [['div', {'class': 'b-material-head__authors-item'}]]
        self.tags = [['a',{'class':'b-material-wrapper__rubric-link'}]]


class Gks(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'gks.ru'
        self.title = []
        self.subtitle = []
        self.articledate = []
        self.text =  [['table', {'class': 'MsoTableGrid'}, 'p']]
        self.hrefs = [['table', {'class': 'MsoTableGrid'}, 'a']]
        self.author = []
        self.tags = []


class Sportbc(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'sport.rbc.ru'
        self.title = [['div',{'class':'article__header__title'}, 'span']]
        self.subtitle = [['div',{'class':'article__text__overview'}]]
        self.articledate = [['span',{'class':'article__header__date'}]]
        self.text =  [['div', {'class': 'article__text'}, 'p']]
        self.hrefs = [['div', {'class': 'article__text'}, 'a']]
        self.author = []
        self.tags = []


class Novayagazeta(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'novayagazeta.ru'
        self.title = [['h1']]
        self.subtitle = [['p',{'data-reactid':'67'}]]
        self.articledate = [['span', {'class': 'b-material-head__date-day'}]]
        self.text =  [['div',{'id':'selection-range-available'}, 'p']]
        self.hrefs = [['div',{'id':'selection-range-available'}, 'a']]
        self.author = [['span', {'data-reactid': '84'}]]
        self.tags = []


class Tvrain(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'tvrain.ru'
        self.title = [['div',{'class':'document-head__title'},'h1']]
        self.subtitle = [['div',{'class':'document-lead'}]]
        self.articledate = [['span', {'class': 'document-head__date'}]]
        self.text =  [['div',{'class':'article-full__text'},'p']]
        self.hrefs = [['div',{'class':'article-full__text'},'a']]
        self.author = [['p',{'style':'text-align: right;'}, 'em'],['span',{'class':'document-head__people'}, 'a']]
        self.insert = [['blockquote',{}]]
        self.tags = []


class Izvestia(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'izvestia.ru'
        self.title = [['h1',{'itemprop':'headline'}]]
        self.subtitle = [['div',{'class':'page_subtitle'}]]
        self.articledate = [['div', {'class': 'article_page__left__top__time__label'}, 'time']]
        self.text =   [['article', {}, 'p']]
        self.hrefs = [['article', {}, 'a']]
        self.author = [['div',{'itemprop':'author'}, 'a']]
        # self.rubrics = [['div',{'class':'rubrics_btn'}]]
        self.tags = []


class Iz(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'iz.ru'
        self.title = [['h1',{'itemprop':'headline'}]]
        self.subtitle = [['div',{'class':'page_subtitle'}]]
        self.articledate = [['div', {'class': 'article_page__left__top__time__label'}, 'time']]
        self.text =   [['article', {}, 'p']]
        self.hrefs = [['article', {}, 'a']]
        self.author = [['div',{'itemprop':'author'}, 'a']]
        # self.rubrics = [['div',{'class':'rubrics_btn'}]]
        self.tags = []

class Pravogov(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'publication.pravo.gov.ru'
        self.title = [['span',{'class':'doccaption'}]]
        self.subtitle = []
        self.articledate = [['span', {'class': 'information2'}]]
        self.text =  []
        self.hrefs = [['a',{'title':'PDF-файл'}]]
        self.author = []
        self.tags = []

class Thebell(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'thebell.io'
        self.title = [['h1',{}]]
        self.subtitle = [['p',{'id':'node1'}]]
        self.articledate = [['span', {'class': 'post__about mb-show'}]]
        self.text =  [['article',{},'p']]
        self.hrefs = [['article',{},'a']]
        self.author = []
        self.tags = []


class Zonamedia(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'zona.media'
        self.title = [['header',{'class':'mz-publish__title'}]]
        self.subtitle = []
        self.articledate = [['div', {'class': 'mz-publish-meta__item'}]]
        self.text =  [['section',{'class':'mz-publish__text'},'p'],
        ['div',{'class':'mz-publish-docscite__text'},'p']]
        self.hrefs = [['section',{'class':'mz-publish__text'},'a'],
                    ['div',{'class':'mz-publish-docscite__text'},'a']
                    ]
        self.author = []
        self.tags = []


class Instagram(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'instagram.com'



class Telegram(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 't.me'
        self.title = [['div',{'class':'tgme_widget_message_owner_name'}]]
        self.subtitle = []
        self.articledate = [['a',{'class':'tgme_widget_message_date'}]]
        self.text =  [['div',{'class':'tgme_widget_message_text'}]]
        self.hrefs =  [['div',{'class':'tgme_widget_message_text'},'a']]
        self.author = [['div',{'class':'tgme_widget_message_owner_name'}]]
        self.tags = []


class Habr(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'habr.com'
        self.title = [['span',{'class':'post__title-text'}]]
        self.subtitle = []
        self.articledate = [['span', {'class': 'post__time'}, False, 'data-time_published']]
        self.text =  [['div',{'class':'post__body_full'}]]
        self.hrefs = [['div',{'class':'post__body_full'}, 'a']]
        self.author = [['span',{'class':'user-info__nickname'}]]
        self.tags = [['li',{'class':'inline-list__item_tag'}]]


class Pikabu(NewsParser):
    def __init__(self):
        """Constructor"""
        self.media = 'pikabu.ru'
        self.title = [['h1',{'class':'story__title'}]]
        self.subtitle = []
        self.articledate = [['time', {'class': 'story__datetime'}, False, 'datetime']]
        self.text =  [['div',{'class':'story__content-inner'}]]
        self.hrefs = [['div',{'class':'story__content-inner'}, 'a']]
        self.author = [['a',{'class':'user__nick'}]]
        self.tags = [['div',{'class':'story__tags'}]]


        # [{'block':'div','block_attr':{'class':'story__content-inner'},'block_elements':'a','attr_val':''}]
