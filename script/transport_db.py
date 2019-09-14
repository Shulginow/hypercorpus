def move_df():
    processed_links = mongo.db.df.find({})
    # processed_links = [i for i in processed_links if]

    data_df = pd.DataFrame([i for i in processed_links] )
    data_df = data_df.fillna(0)

    data_df = data_df.drop_duplicates(subset=['document_url','source_url','link_text'])
    #processed_links = data_df.to_dict()
        #with MSQLDB.atomic():
            #LinkStat.insert_many(processed_links).on_conflict('replace').execute()
    for index, pl in data_df.iterrows():
        try:
            pl  = pl.to_dict()
            LinkStat.insert(**pl).on_conflict('replace').execute()

        except Exception as e:
            print(str(e))

    return str(pl)
