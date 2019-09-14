import config
import numpy as np
import os
import pandas as pd
import requests
import urllib.request


from bs4 import BeautifulSoup
from lxml import etree
from models import *
from txt import semanticProcessor


class offersProcessor:

    def __init__(self):
        """Constructor"""
        self.offers_store = config.offers_store
        self.offers_site  = config.offers_site
        self.img_path = config.img_path
        self.stores_path = config.stores_path
        self.semanticProc = semanticProcessor()
        pass


    def getOffers(self):
        """Получение списка товаров из двух выгрузок"""

        """!!! Важно. Перед загрузкой обновить выгрузку иначе слетают картинки !!!"""

        c = []
        try:
            store = self.getOffersStore(self.offers_store)
            site = self.getOffersSite(self.offers_site)

            offers = pd.merge(store, site, on='name', how='left')

            offers = self.OffersAddUid(offers)

            offers = offers.where(pd.notnull(offers), None)

            if len(store) > 0 and len(site) > 0:
                response = self.saveOffers(offers)
                response = str(response)

        except Exception as e:
            response = str(e)

        return response


    def updateStorePrices(self):
        """"""
        cols = ['xml_id','name','origin','bulk','alcohol',
        'prop30','prop37','description_2','combination',
        'prop41','prop42','prop45','prop46','prop47','group0','group1','group2']

        new_names = {'IE_XML_ID':'xml_id', 'IE_NAME':'name','IP_PROP31':'origin','IP_PROP32':'bulk',
         'IP_PROP33':'alcohol','IP_PROP39':'combination', 'IP_PROP39':'combination', 'IP_PROP38':'description_2',
         'IC_GROUP1':'group1','IC_GROUP0':'group0','IC_GROUP2':'group2'}

        company_offer = pd.read_csv(config.offers_store, sep=';')
        company_offer = company_offer.rename(columns=new_names)
        company_offer.columns = map(str.lower, company_offer.columns)
        company_offer = company_offer.rename(columns=lambda n: n.replace('ip_', ''))
        company_offer[:10].to_excel('co.xlsx')
        return company_offer[:3]


    def saveOffers(self,offers_data):
        """Сохранение товаров"""
        c = []

        q = OffersBeta.delete()
        q.execute()

        for index, row in offers_data.iterrows():
            try:
                row = self.getOfferPic(row)
                data_dict = row.to_dict()
                OffersBeta.create(**data_dict)
                c.append('1')
            except Exception as e:

                c.append(str(e))

        updated = self.getOffersUpdate()

        #c.append(updated)
        #         added = self.getOffersAddfields()
        #         c.append(added)
        return c



    def OffersAddFeatures(self, company_offer):
        """Обработка свойств товаров из выгрузки"""

        company_offer = self.OffersSetAlcoholCluster(company_offer)
        company_offer = self.OffersSetCategory(company_offer)

        company_offer = self.OffersFeatureNormalize(company_offer, ['prop41','prop42','prop45','prop47','alcohol_cluster'])

        company_offer['bulk'] = company_offer['bulk'].astype('str').apply(lambda x: x.replace(',', '.')).fillna(0).astype('float')

        company_offer = company_offer.where(pd.notnull(company_offer), None)

        return company_offer


    def OffersFeatureNormalize(self, company_offer, columns):
        """Создание дублей колонок, с названиями признаков в нормальной форме"""
        for c in columns:
            add_c = c + '_s'
            try:
                company_offer[add_c] = company_offer[c].fillna('').astype('str').apply(self.semanticProc.normalise)
            except Exception as e:
                company_offer[add_c] = str(e)

        return company_offer



    def OffersAddUid(self, offers):
        """"""
        offers.category_id = offers.category_id.fillna(999)
        try:
            offers['u_id'] = offers.category_id.astype('str') + offers.xml_id.astype('str').apply(lambda x: x.zfill(9))
        except:
            offers['u_id'] = '9999' + offers.xml_id.astype('str').apply(lambda x: x.zfill(9))


        return offers


    def OffersSetCategory(self, offers):
        """Установка категорий для отдельных групп товаров"""

        offers.loc[offers.group1.isnull(), 'group1'] = offers.loc[offers.group1.isnull(), 'group0']
        for i in ['Соки']:
            offers.loc[offers.group1.str.contains(i), 'group1'] = i

        categories = ['Граппа','Чача','Кашаса','Зефир','Мармелад']

        for i in categories:

            offers.loc[offers.name.str.contains(i), 'group1'] = i

        return offers



    def OffersSetAlcoholCluster(self, offers):
        """Добавление обобщенного признака крепости"""

        offers.alcohol = offers.alcohol.fillna('0').str.replace(',', '.').astype(np.float32).apply(lambda x: round(x, 1))

        alco_clusters = [[0, 0.99,'Безалкогольное', 'Пиво'], [0.99, 4.2,'Лёгкое', 'Пиво'],
            [4.2, 5.9, 'Среднее', 'Пиво'], [5.9, 7.4, 'Крепкое', 'Пиво'], [7.5, 1000, 'Очень крепкое', 'Пиво']]

        for i in alco_clusters:

            offers.loc[((offers.group1 == i[3])&(offers.alcohol > i[0])&(offers.alcohol < i[1])), 'alcohol_cluster'] = i[2]

        return offers



    def getOffersStore(self,url):
        """Получение данных о  товарах из csv-файла"""

        cols = ['xml_id','name','origin','bulk','alcohol',
        'prop30','prop37','description_2','combination',
        'prop41','prop42','prop45','prop46','prop47','group0','group1','group2']

        new_names = {'IE_XML_ID':'xml_id', 'IE_NAME':'name','IP_PROP31':'origin','IP_PROP32':'bulk',
         'IP_PROP33':'alcohol','IP_PROP39':'combination', 'IP_PROP39':'combination', 'IP_PROP38':'description_2',
         'IC_GROUP1':'group1','IC_GROUP0':'group0','IC_GROUP2':'group2'}

        company_offer = pd.read_csv(url, sep=';')

        company_offer = company_offer.rename(columns=new_names)
        company_offer.columns = map(str.lower, company_offer.columns)
        company_offer = company_offer.rename(columns=lambda n: n.replace('ip_', ''))

        company_offer = company_offer[cols]


        company_offer = self.OffersAddFeatures(company_offer)

        return company_offer


    def getPrices(self):
        """Получаем цены в магазинах города"""

        url = self.offers_store
        response = 'Цены обновлены'

        try:
            company_offer = pd.read_csv(url, sep=';')
            select_columns = [x for x in company_offer.columns  if  'CV_PRICE' in x] + ['IE_XML_ID']
            df = company_offer[select_columns].melt(id_vars = 'IE_XML_ID', var_name='store_id', value_name='price')
            df = df[~df.price.isnull()]
            df.columns = ['xml_id','store_id','price']
            df.store_id = df.store_id.str.extract('(\d+)')

            for c in df.columns:
                df[c] = df[c].astype('int')

            df['u_id'] = df.xml_id.astype('str') + '0000' + df.store_id.astype('str')
            df['u_id']  = df['u_id'].astype('int')

            self.savePrices(df)

        except Exception as e:
                response = str(e)

        return response



    def savePrices(self,offers_data):
        """Сохранение цен товаров"""
        c = []

        q = OffersPrice.delete()
        q.execute()

        for index, row in offers_data.iterrows():
            data_dict = row.to_dict()
            try:

                OffersPrice.create(**data_dict)
                c.append(1)
            except Exception as e:

                c.append(str(e))

        return str(c)



    def getOfferPic(self, offer):

        if offer.picture_url is not None:

            directory = self.img_path+str(offer['category_id'])

            if not os.path.exists(directory):

                os.makedirs(directory)

            pic_path = offer.picture_url.split('/')
            filename = directory+'/'+'/'.join(pic_path[-1:])

            u = urllib.request.urlopen(offer['picture_url'])
            info = u.info()

            if int(info["Content-Length"]) > 0:

                data = urllib.request.urlretrieve(offer['picture_url'], filename)
                offer['picture_file'] = filename

        return offer



    def getOffersUpdate(self):
        """Загрузка картинок на сервер и в базу"""
        query = OffersBeta.select()
        r = 'ok'
        for offer in query:
            try:
                if offer.picture_url:

                    directory = self.img_path+str(offer.category_id)

                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    pic_path = offer.picture_url.split('/')
                    filename = directory+'/'+'/'.join(pic_path[-1:])

                    u = urllib.request.urlopen(offer.picture_url)
                    info = u.info()

                    if int(info["Content-Length"]) > 0:

                        data = urllib.request.urlretrieve(offer.picture_url, filename)
                        offer.picture_file = filename
                        offer.save()

                    #r.append()
            except Exception as e:
                r = str(e)
                break
        return r


#     def getOffersAddfields(self):
#         """Добавление полей в простой форме"""
#         query = OffersBeta.select().where(OffersBeta.picture_file.is_null(False))
#         r = 'ok'
#         for offer in query:
#
#             try:
#                 if offer.prop47:
#                     offer.prop47_s = self.semanticProc.normalise(offer.prop47)
#
#                 if offer.prop45:
#                     offer.prop45_s = self.semanticProc.normalise(offer.prop45)
#
#                 if offer.prop42:
#                     offer.prop42_s = self.semanticProc.normalise(offer.prop42)
#
#                 if offer.prop41:
#                     offer.prop41_s = self.semanticProc.normalise(offer.prop41)
#
#
#                 offer.save()
#                 #for o in [[offer.prop47, offer.prop47_s],[offer.prop42, offer.prop42_s],[offer.prop41, offer.prop41_s]]:
#                 #    if o[0]:
#                 #        o[1] = self.normalise(o[0])
#                 #        offer.save()
#             except Exception as e:
#                 r = str(e)
#                 #break
#         return r


    def getOffersSite(self,url):
        """Получение товаров с картинками"""
        r = requests.get(url)
        x = r.text
        soup=BeautifulSoup(x, "lxml")

        offer_list = []
        for offer in soup.find_all('offer'):

            try:
                category_id = offer.find('categoryid').text
            except:
                category_id = 0
            try:
                url = offer.find('url').text
            except:
                url = None
            try:
                name = offer.find('name').text
            except:
                name = None
            try:
                picture_url = offer.find('picture').text
            except:
                picture_url = None

#             if picture_url is not None:
#                 picture_file = self.getOffersPicture(picture_url, category_id)
#             else:
#                 picture_file = None

            try:
                price = offer.find('price').text
            except:
                price = 0

            elements = [offer['id'], category_id, url, name, picture_url, price]

            offer_list.append(elements)

        xml_offer = pd.DataFrame(offer_list, columns=['site_id', 'category_id', 'url','name', 'picture_url','price'])
        #xml_offer = xml_offer.astype(object).where(pd.notnull(xml_offer), None)
        xml_offer.loc[xml_offer['url'].isnull(), 'url'] = None
        xml_offer.loc[xml_offer['picture_url'].isnull(), 'picture_url'] = None
        #xml_offer['picture_url'] = xml_offer['picture_url'].fillna(None)
        return xml_offer


    def showFeatures(self):
        """"""
        try:
            features = [['origin',OffersBeta.origin],['prop47',OffersBeta.prop47],['prop45',OffersBeta.prop45],['prop42',OffersBeta.prop42],['prop41',OffersBeta.prop41],['bulk',OffersBeta.bulk],['alcohol',OffersBeta.alcohol]]

            contain = {}
            for f in features:
                query = (OffersBeta.select(f[1]).distinct()).dicts()

                feature_name = []
                for i in query:
                    text = self.semanticProc.normalise(i[f[0]])
                    feature_name.append(text)

                contain[f[0]] = feature_name

            r = str(feature_name)
        except Exception as e:
            r = str(e)
        return r


    def showCategories(self):
        """"""
        try:
            categories = []
            query = (OffersBeta.select(OffersBeta.alcohol).order_by(OffersBeta.alcohol).distinct()).dicts()

            for i in query:
                categories.append(i['alcohol'])
            r = str(categories)
        except Exception as e:
            r = str(e)
        return r


    def getStores(self):
        """Загрузка данных о магазинах"""

        response = 'x'
        try:

            source = self.stores_path + 'cat_store_list.csv'

            stores_data = pd.read_csv(source)
            stores_data.lat = stores_data.lat.astype('float').apply(lambda x: round(x, 8))
            stores_data.lng = stores_data.lng.astype('float').apply(lambda x: round(x, 8))
            response = stores_data.shape[0]

            for index, row in stores_data.iterrows():
                data_dict = row.to_dict()
                StoreAddress.create(**data_dict)

        except Exception as e:
            response = str(e)

        return response


    def update_discounts(self):
        '''Обновление скидок в базе данных по товарам'''

        u = OffersBeta.update(price_action=0)
        u.execute()

        for n in range(1,50):

            discounts_data = self.HtmlParser.get_discounts(page=n)
            if len(discounts_data) > 0:

                for offer in discounts_data:
                    u = OffersBeta.update(price_action=offer[3]).where(OffersBeta.site_id == offer[1])
                    u.execute()
        return 1
