from ufal.udpipe import Model, Pipeline, Sentence



class Vectors:
    def __init__(self):

        ud_model_path = '../models/udpipe_syntagrus.model'
        self.ud_model = Model.load(ud_model_path)

        w2v_model_path = '../models/ruscorpora_upos_skipgram_300_5_2018.vec.gz'
        self.w2v_model = gensim.models.KeyedVectors.load_word2vec_format(w2v_model_path)

        self.process_pipeline = Pipeline(self.ud_model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')


    def tag_ud(self, text='Текст нужно передать функции в виде строки', pos=True):
        """
        Разметка на части речи
        если частеречные тэги не нужны (например, их нет в модели), выставьте pos=False
        в этом случае на выход будут поданы только леммы
        """

        # обрабатываем текст, получаем результат в формате conllu:
        processed = self.process_pipeline.process(text)
        # пропускаем строки со служебной информацией:
        content = [l for l in processed.split('\n') if not l.startswith('#')]
        # извлекаем из обработанного текста лемму и тэг
        tagged = [w.split('\t')[2].lower() + '_' + w.split('\t')[3] for w in content if w]

        tagged_propn = []
        propn = []
        for t in tagged:
            if t.endswith('PROPN'):
                if propn:
                    propn.append(t)
                else:
                    propn = [t]
            elif t.endswith('PUNCT'):
                propn = []
                continue  # я здесь пропускаю знаки препинания, но вы можете поступить по-другому
            else:
                if len(propn) > 1:
                    name = '::'.join([x.split('_')[0] for x in propn]) + '_PROPN'
                    tagged_propn.append(name)
                elif len(propn) == 1:
                    tagged_propn.append(propn[0])
                tagged_propn.append(t)
                propn = []
        if not pos:
            tagged_propn = [t.split('_')[0] for t in tagged_propn]

        return tagged_propn


    def text_pos_add(self, text):
        """добавление части речи к тексту - применение функции tag_ud"""
        text_tagged = [i for i in self.tag_ud(text=text) if i in self.w2v_model.index2word]
        return text_tagged


    def get_w2v_mean_similarity(self, t1, t2):
        """получение схожести двух массивов слов"""
        s_data = []
        for i in t1:
            for j in t2:
                try:
                    s = self.w2v_model.wv.similarity(w1=i, w2=j)
                    s_data.append(s)
                except:
                     pass

        r = np.array(s_data).mean()
        return r


    def get_max_similarity(self, source, link):
        """поиск максимальной схожести слов каждый с каждым"""
        sim = 0
        pair = []
        #print('чек', source, link)
        if min(len(source), len(link)) >0:
            for s in source:
                for l in link:
                    #print('чек', l, s)
                    i_sim = get_w2v_mean_similarity([s], [l])
                    #print('чек', i_sim)
                    if i_sim > sim:
                        sim = i_sim
                        pair = [l,s,sim]
        return pair
