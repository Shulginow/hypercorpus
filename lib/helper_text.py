import re
import nltk
import pymorphy2
import operator
from nltk.corpus import stopwords
from bs4 import BeautifulSoup


class TxtParser:

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()

        sw = stopwords.words('russian')
        sw.extend(['это','который', 'the','вместо','около','весь'])
        self.stopwords = set(sw)


    def clean_html(self, t):

        soup = BeautifulSoup(t, "lxml")
        return soup.text


    def text_normalise(self, t, use_stop_words = True):
        """Приведение всех слов в нормальный вид и удаление стоп-слов"""

        # t = self.tagClean(t)

        # stop_words = ['а', 'бы', 'в', 'во', 'вот', 'для', 'до', 'если', 'же', 'за','чем','также','этот',
        #               'и', 'из', 'или', 'к', 'как', 'ко', 'между', 'на', 'над', 'но', 'о', 'он', 'об', 'около', 'от',
        #               'по', 'под', 'при', 'про', 'с', 'со', 'среди', 'то', 'у', 'чтобы', 'это', 'с', 'что']


        nt = nltk.word_tokenize(t)
        nt_clean = list(self.morph.parse(part)[0].normal_form for part in nt if part.isalpha())

        if use_stop_words:
            stop_words = self.stopwords
        else:
            stop_words = []

        nt_clean = list(x for x in nt_clean if not x.lower() in stop_words)

        text_normalised = ' '.join(nt_clean)
        return text_normalised


    def set_lemmas_freq(self, lemmas_main):
        """сортировка лемм по частоте с посмощью библиотеки nltk"""

        lemmas_main = self.set_text(lemmas_main)

        lemmaFreq = nltk.FreqDist(lemmas_main)
        lemmaFreq = sorted(lemmaFreq.items(), key=operator.itemgetter(1)).reverse()

        return lemmaFreq


    def set_text(self, text):
        """предобработка текста"""
        text_sp = re.findall('\w\w+', text)
        text_sp = list(map(str.lower, text_sp))
        # text_sp = (' '.join(text_sp))
        return text_sp


    def define_link_norm(self, h_text):
        """Получение нормализованной версии слова"""

        h_text_norm = self.text_normalise(h_text, use_stop_words=False)

        h_text_norm = h_text_norm.strip()
        return h_text_norm


    def morph_analyse(self, word):
        """Очистка от тегов"""

        ma = self.morph.parse(word)[0]

        response = [

            ma.tag.POS,
            ma.tag.animacy,
            ma.tag.aspect,
            ma.tag.case,
            ma.tag.gender,
            ma.tag.mood,
            ma.tag.tense,
            ma.tag.person,
            ma.tag.number,
            ma.tag.transitivity,
            ma.tag.voice,
            ma.score
        ]

        heads = [
            'pos','animacy','aspect', 'case','gender','mood','tense','person','number',
            'transitivity','voice','score'
        ]


        return response,heads

# tp = TxtParser()
# print(tp.set_text('sasSS asaas'))
