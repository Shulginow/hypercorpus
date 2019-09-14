import sys
sys.path.insert(0, '..')

import pymongo
from tqdm import tqdm
import pandas as pd

from models import *


mgclient = pymongo.MongoClient("mongodb://localhost:27017/")
sp_db = mgclient["semproxydb"]


def move_data():
    for i in range(0, 200000, 1000):

        print(i)

        text_data = sp_db.text_total.find({}).skip(i).limit(1000)

        data_df = pd.DataFrame([i for i in text_data] )
        # data_df = data_df.fillna(0)
        #
        drop_names = ['rubrics','insert']

        for i in drop_names:
            if i in data_df.columns:
                data_df = data_df.drop([i], axis=1)

        data_df = data_df.drop_duplicates(subset=['url'])

        #processed_links = data_df.to_dict()
            #with MSQLDB.atomic():
                #LinkStat.insert_many(processed_links).on_conflict('replace').execute()

        for index, pl in tqdm(data_df.iterrows()):
            try:
                pl  = pl.to_dict()
                Content.insert(**pl).on_conflict('replace').execute()

            except Exception as e:
                print(str(e))

    return str(pl)

if __name__ == '__main__':
    move_data()
