from peewee import *
from datetime import datetime
import config_db

# MSQLDB = MySQLDatabase(
#     database='hyperco',
#     user = 'root',
#     password = "powerd2t2",
#     host='localhost'
# )

MSQLDB = MySQLDatabase(
    database=config_db.db_n,
    user = config_db.db_u,
    password = config_db.db_p,
    host='localhost'
)

class BaseModel(Model):
    class Meta:
        database = MSQLDB


class LinkStatOut(BaseModel):

    document_domain = CharField()
    document_link_html = TextField()
    document_url = CharField(1000)
    link_text = TextField()
    source_domain = CharField()
    source_url = CharField()
    link_sentense = TextField()
    
    class Meta:
        database = MSQLDB
        table_name = 'link_stat_out'


class LinkStat(BaseModel):

    _id = CharField(unique = True)
    document_domain = CharField()
    document_link_html = TextField()
    document_text_tfidf_top = CharField(1000)
    document_url = CharField(1000)
    link_norm = CharField()
    link_norm_count = IntegerField()
    link_ps_ADJ = IntegerField()
    link_ps_ADV = IntegerField()
    link_ps_INTJ = IntegerField()
    link_ps_NOUN = IntegerField()
    link_ps_NUM = IntegerField()
    link_ps_PROPN = IntegerField()
    link_ps_VERB = IntegerField()
    link_ps_SYM = IntegerField()
    link_sentense = TextField()
    link_tagged = CharField()
    link_text = TextField()
    sim_domain_link = DecimalField()
    sim_stext_link = DecimalField()
    sim_stext_lsentense = DecimalField()
    sim_stfidf10_ltext = DecimalField()
    sim_stfidf5_link = DecimalField()
    sim_stfidf5_link_max = DecimalField()
    sim_stfidf5_link_pair = CharField()
    sim_stfidf_ltfidf = DecimalField()
    sim_stitle_link = DecimalField()
    sim_stitle_lsentense = DecimalField()
    source_domain = CharField()
    source_id = CharField()
    source_subtitle_norm = TextField()
    source_text_tfidf_top = CharField(1000)
    source_title = TextField()
    source_title_norm = TextField()
    source_url = CharField()
    text_id = CharField()
    source_index = IntegerField()
    link_is_publisher_name = IntegerField()
    sim_text_w_tfifd = DecimalField()
    sim_stext_lsentense_w_tfifd = DecimalField()
    link_is_root = IntegerField()
    link_succersors = TextField()
    links_pos = CharField()
    link_title_equals = IntegerField()
    document_title = CharField(500)
    sim_sp0_link_sentense = DecimalField()
    sim_sp1_link_sentense = DecimalField()
    sim_sp2_link_sentense = DecimalField()
    sim_sp3_link_sentense = DecimalField()
    sim_sp4_link_sentense = DecimalField()
    sim_sp5_link_sentense = DecimalField()
    sim_sp6_link_sentense = DecimalField()

    class Meta:
        database = MSQLDB
        table_name = 'link_stat'


class LinkQueque(BaseModel):

    _id = CharField(unique = True)
    url = CharField(1000)
    url_domain = CharField(300)
    source = CharField(1000)
    source_domain = CharField(300)
    status = CharField(50)

    class Meta:
        database = MSQLDB
        table_name = 'link_queque'



class Content(BaseModel):

    url = CharField(1000)
    url_key = CharField(300)
    hrefs = TextField()
    text = TextField()
    articledate = CharField()
    title = CharField(1000)
    subtitle = TextField()
    author = CharField(500)
    tags = CharField(1000)
    media = CharField()
    text_normalized = TextField()
    title_normalized = TextField()
    subtitle_normalized = TextField()
    status = CharField(45)


    class Meta:
        database = MSQLDB
        table_name = 'content'


class TermsDf(BaseModel):

    term = CharField(1000)
    df = IntegerField()

    class Meta:
        database = MSQLDB
        table_name = 'terms_df'
