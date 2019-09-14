from peewee import *
from datetime import datetime

import logging

logging.basicConfig(filename="filter.log", level=logging.INFO)

logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


DB = MySQLDatabase(
    database='dilandb',
    user = 'root',
    password = "powerd2t2",
    host='localhost'
)


# DB = MySQLDatabase(
#     'vstoch2s_process',
#     user = 'vstoch2s_process',
#     password = r"*%2%f4gn",
#     host='localhost'
# )



class BaseModel(Model):
    class Meta:
        database = DB

class ChatUser(BaseModel):
    id = BigIntegerField(unique=True)
    #chat_id = BigIntegerField(unique=True))
    first_name = CharField(max_length = 225, null =True)
    last_name = CharField(max_length = 225, null =True)
    username = CharField(max_length = 225, null =True)
    phone = CharField(max_length = 225, null =True)
    birth = CharField(max_length = 100, null =True)
    subscribed = IntegerField()

    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = DB
        table_name = 'chat_user'


class Campaign(BaseModel):

    id = AutoField()
    discount_id = BigIntegerField()
    name = CharField(max_length = 225, null =True)
    url = CharField(max_length = 225, null =True)
    text = CharField(max_length = 225, null =True)
    status = CharField(max_length = 100, null =True)
    is_sent = IntegerField()
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DB
        table_name = 'campaigns'


class CampaignSend(BaseModel):

    campaign_id = BigIntegerField()
    user_id = BigIntegerField()

    class Meta:
        database = DB
        table_name = 'campaigns_send'


class CampaignList(BaseModel):

    campaign_id = BigIntegerField(unique=True)
    user_id = BigIntegerField(unique=True)

    class Meta:
        database = DB
        table_name = 'campaigns_list'
        primary_key = CompositeKey('campaign_id', 'user_id')


class ChatGeo(BaseModel):
    id = AutoField()
    chatuser = ForeignKeyField(ChatUser, backref='geopositions')
    lat = CharField(max_length = 225, null =True)
    lng = CharField(max_length = 225, null =True)
    location = CharField(max_length = 225, null =True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DB
        table_name = 'chat_geo'


class ChatFilter(BaseModel):
    id = AutoField()
    chatuser = ForeignKeyField(ChatUser, backref='filter')
    filter = CharField(max_length = 500, null =True)
    category = CharField(max_length = 500, null =True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DB
        table_name = 'chat_filter'


class ChatFunnel(BaseModel):
    id = AutoField() #уникальный id
    chatuser = ForeignKeyField(ChatUser, backref='funnels')
    type = IntegerField() #запрос/ответ
    chatfunnel = CharField(50)
    message = TextField()
    message_id = IntegerField()
    offer_id = IntegerField()
    photo_id = CharField(500)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = DB
        table_name = 'chat_funnel'


class Loghook(BaseModel):
    id = AutoField() #уникальный id
    chat_id = BigIntegerField()
    fulljson = TextField()
    created_at = DateTimeField(default=datetime.now)


class ChatSupport(BaseModel):
    """"""
    id = AutoField() #уникальный id
    questioner_chat_id = BigIntegerField ()
    questioner_message_id = BigIntegerField ()
    manager_message_id = BigIntegerField ()
    message = TextField()
    created_at = DateTimeField(default=datetime.now)


class StoreDiscounts(BaseModel):
    """"""
    id = AutoField() #уникальный id
    description = TextField()
    active = IntegerField()
    picture_id = TextField()
    text_full = TextField()
    chat_id = BigIntegerField()
    created_at = DateTimeField(default=datetime.now)


class ShopAddress(BaseModel):
    """"""
    id = AutoField() #уникальный id
    region = TextField(70)
    city = TextField(70)
    street = TextField(100)
    lat = TextField(30)
    lng = TextField(30)
    created_at = DateTimeField(default=datetime.now)


class StoreAddress(BaseModel):
    """"""
    id = IntegerField(unique=True) #уникальный id
    region = TextField(70)
    city = TextField(70)
    street = TextField(100)
    title = TextField(100)
    active = IntegerField()
    changed = DateTimeField()
    code = TextField(100)
    outer_id = IntegerField()
    phone = TextField(100)
    lng = TextField(30)
    lat = TextField(30)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = DB
        table_name = 'store_address'


class ChatReplic(BaseModel):
    """"""
    id = AutoField() #уникальный id
    funnel = TextField(70)
    keywords = TextField(800)
    replic = TextField(500)
    created_at = DateTimeField(default=datetime.now)
    class Meta:
        database = DB
        table_name = 'chat_replics'

class Offers(BaseModel):
    u_id = BigIntegerField(unique=True)
    xml_id = IntegerField()
    name = CharField(null = True)
    site_id = CharField(null = True)
    url = CharField(300)
    picture_url = CharField(null = True)
    picture_id = CharField(null = True)
    category_id = IntegerField()
    ie_preview_text= TextField(null = True)
    ie_detail_text= TextField(null = True)
    origin = CharField(100, null = True)
    bulk = CharField(25, null = True)
    alcohol = CharField(10, null = True)
    prop30 = CharField(100, null = True)
    prop37 = CharField(100, null = True)
    description_2 = CharField(1000, null = True)
    combination = CharField(1000, null = True)
    prop40 = CharField(null = True)
    prop41 = CharField(null = True)
    prop42 = CharField(null = True)
    prop43 = CharField(null = True)
    prop44 = CharField(null = True)
    prop45 = CharField(null = True)
    prop46 = CharField(null = True)
    prop47 = CharField(null = True)
    prop48 = CharField(null = True)
    prop49 = CharField(null = True)
    prop50 = CharField(null = True)
    group0 = CharField(null = True)
    group1 = CharField(null = True)
    group2 = CharField(null = True)

    created_at = DateTimeField(default=datetime.now)


class OffersPrice(BaseModel):

    u_id = CharField(unique = True)
    xml_id = IntegerField()
    store_id = IntegerField(null = True)
    price = IntegerField(null = True)

    class Meta:
        database = DB
        table_name = 'offers_price'


class OffersBeta(BaseModel):
    u_id = BigIntegerField(unique=True)
    xml_id = IntegerField()
    name = CharField(null = True)
    site_id = CharField(null = True)
    url = CharField(300)
    price = CharField(null = True)
    price_action = IntegerField(null = True)
    picture_url = CharField(null = True)
    picture_id = CharField(null = True)
    picture_file = CharField(null = True)
    category_id = IntegerField()
    origin = CharField(100, null = True)
    bulk = CharField(25, null = True)
    alcohol = CharField(10, null = True)
    alcohol_cluster = CharField(75, null = True)
    prop30 = CharField(100, null = True)
    prop37 = CharField(100, null = True)
    description_2 = CharField(1000, null = True)
    combination = CharField(1000, null = True)
    prop41 = CharField(null = True)
    prop42 = CharField(null = True)
    prop45 = CharField(null = True)
    prop46 = CharField(null = True)
    prop47 = CharField(null = True)
    group0 = CharField(null = True)
    group1 = CharField(null = True)
    group2 = CharField(null = True)
    prop41_s = CharField(null = True)
    prop42_s = CharField(null = True)
    prop45_s = CharField(null = True)
    prop47_s = CharField(null = True)
    alcohol_cluster_s = CharField(75, null = True)

    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = DB
        table_name = 'offers_beta'


class OffersPicTxt(BaseModel):

    u_id = BigIntegerField(unique=True)
    picture_url = CharField(null = True)
    text  = CharField(1000,null = True)
    text_vec = CharField(2000,null = True)
    name = CharField(null = True)

    class Meta:
        database = DB
        table_name = 'offers_pictxt'
