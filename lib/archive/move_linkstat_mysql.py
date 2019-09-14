import sys
sys.path.insert(0, '..')

import pymongo
from tqdm import tqdm
import pandas as pd
from models import *

mgclient = pymongo.MongoClient("mongodb://localhost:27017/")
sp_db = mgclient["semproxydb"]

def move_data():
    for i in range(0, 60000, 1000):

        text_data = sp_db.links_stat_3.find({}).skip(i).limit(1000)

        data_df = pd.DataFrame([i for i in text_data] )
        data_df = data_df.fillna(0)
        #
        drop_names = ['raw_text_id','text_sim_w_tf_ifd', 'raw_text_if','source_text',
        'source_text_elements_norm','source_text_norm']

        for i in drop_names:
            if i in data_df.columns:
                data_df = data_df.drop([i], axis=1)

        try:
            data_df = data_df.drop_duplicates(subset=['document_url','source_url','link_text'])
        except:
            print('1', str(e))
            data_df = data_df
        #data_df = data_df.fillna(-1)
        for index, pl in tqdm(data_df.iterrows()):

            try:
                pl  = pl.to_dict()
                # print(pl)
                LinkStat.insert(**pl).on_conflict('replace').execute()

            except Exception as e:
                print(str(e), pl)


        #processed_links = data_df.to_dict()
            #with MSQLDB.atomic():
                #LinkStat.insert_many(processed_links).on_conflict('replace').execute()



    return str(pl)

if __name__ == '__main__':
    move_data()
