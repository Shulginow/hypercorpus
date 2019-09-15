import re
from nltk.tokenize import sent_tokenize


class HtmlProcess:
    def __init__(self):
        pass

    def clean_tag(self, t):
        """очистка от всех тегов"""
        p = re.compile(r'<.*?>')
        t = p.sub('', t)

        return t


    # def add_domain(a,host):
    #     """Добавление домена внутренним ссылкам"""
    #
    #     a_domain = self.get_domain(a)
    #     if a_domain is False and len(a) > 3 :
    #         a  = 'http://{}{}'.format(host,a)
    #
    #     return a


    def add_domain(self, a, host):
        """если ссылка на внутреннюю страницу, добавляем домен"""
        if host not in a:
            if re.match('^\/',a):
                a = '{}{}'.format(host,a)
        return a


    def add_http(self, url, media):
        """Добавление http и названия домена"""
        if re.match('^http',url) is None:
            if re.match('\/\w+',url):
                url = 'http://{}{}'.format(media,url)
            else:
                url = False
                pass
        return url


    def clean_html(self, html):
        """очистка мусора из текста"""
        expression = re.compile('(<.*?>,\s<.*?>|<.*?>|\[|\])')
        cleantext = re.sub(expression, '', html)

        expression = re.compile('^,')
        cleantext = re.sub(expression, '', cleantext)

        return cleantext.strip()


    def clean_morespaces(self,html):
        """Преобразование двойных пробелов в один"""
        expression = re.compile('\s\s+')
        cleantext = re.sub(expression, '\s', html)

        return cleantext


    def define_link_position(self,txt, link_text):
        """Определение позиции ссылки"""
        txt = re.sub(r'<[\s]*a[\s]*href[\s]*=[^>]+>[\s]*{}[\s]*<[\s]*\/[\s]*a[\s]*>'.format(link_text), '<>', txt)

        if re.search(r'<>', txt):
            start, end = re.search(r'<>', txt).span()
        else:
            start = -1
        return start


    # def define_link_domain(self,h_url):
    #     """Определение домена ссылки"""
    #     try:
    #         h_url = re.sub(r'http[s]*://http[s]*://', 'http://', h_url)
    #
    #         h_domain = re.search(r'//[^/]+', h_url).group(0)[2:]
    #         h_domain = re.sub(r'^www.', '', h_domain)
    #
    #     except Exception as e:
    #         h_domain = str(e)
    #
    #     return h_url, h_domain


    # def get_domain(self, url):
    #     """Получение домена ссылки"""
    #     domain = re.search('((p|s)://|www\.)[a-z-A-Z0-9\-.]+',url)
    #     try:
    #         domain = domain.group()[4:]
    #         domain = re.sub('^www\.', '', domain)
    #     except:
    #         domain = False
    #
    #     return domain

    def get_host(self,url):
        """Получение домена ссылки"""

        x = re.findall('//(?:www\.)?[^\/]+',url)
        if len(x):
            d =x[0][2:].replace('www.','')
        else:
            d = False

        # url = self.clean_http(url)
        # domain = re.search('[^/]+',url)
        # try:
        #     domain = domain.group()
        # except:
        #     domain = False

        return d


    def clean_http(self,h_url):
        """Определение домена ссылки"""
        try:
            h_url = re.sub(r'(http[s]*:)*(\/\/)*(www\.|)*', '', h_url)
        except Exception as e:
            print(str(e))

        return h_url


    def define_link_sentence(self, text, href_code):
        '''Определяем предложение ссылки'''

        text = str(text)
        href_code = str(href_code)
        text_cl = re.sub('<(\/|)(p|div).*?>', '', text)

        text_tokenized = sent_tokenize(text_cl)

        response = False
        for sentense in text_tokenized:
             if href_code in sentense:
                response = sentense

        return response


    # def define_link_sentence(self,h_text, h_url):
    #     """Определение предложения ссылки"""
    #     try:
    #         # re_cond = r'[^.]+' + re.escape(h_url) + r'[^>]+[^.]+'
    #         re_cond = r'[^.]+' + re.escape(h_url) + r'[^>\.]+'
    #         h_sentence = re.search(re_cond, h_text).group(0)
    #     except:
    #         h_sentence = '!'
    #
    #     h_sentence = self.clean_morespaces(h_sentence)
    #
    #     return h_sentence.strip()


    def is_anchor_link(self,text):
        '''Проверка, есть ли в ссылке анкор'''

        response =False
        h_text = re.search(r'>[A-Za-zА-Яа-я0-9-_!?«»\"]+', text)
        if h_text:
            response =True

        return response


    def define_link_href(self,h):
        """Определение адреса ссылки"""
        try:
            h_href = re.findall('<a[^>]+href=\"(.*?)\"[^>]*>', h)
        except:
            h_href = []

        return h_href


    def define_link_text(self,h):
        """Определение текста ссылки"""
        try:
            h_text = re.search(r'[>].+', h).group(0)[1:].strip()
        except:
            h_text = '!'

        h_text_list = h_text.split(' ')
        return h_text_list


    def define_links_text(self,h):
        """Определение текста всех ссылок в тексте"""
        try:
            h_text = re.findall('<a[^>]+>(.+?)</a>', h)
        except:
            h_text = []
        return h_text


    def text_check_content(self,text):
        """Проверка текста 1 - на то что это не просто сборник ссылок

        0 - слишком много ссылок
        1 - все ок
        2 - нет текста
        3 - ссылок нет
        """

        response = 0
        link_text = ' '.join(helper_html.define_links_text(text))
        total_text =  helper_html.clean_html(text)

        if len(link_text) == 0:
            return 3
        if len(total_text) == 0:
            return 2

        link_ratio = len(link_text) / len(total_text)

        if link_ratio < .5 and link_ratio > 0:
            response = 1

        return response
