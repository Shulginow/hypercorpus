import sys
sys.path.insert(0, '..')
from models import *

def run():
    ulrs_saved = []

    urls = Content.select(Content.url_key, Content.id).where(~Content.url_key.is_null()).distinct().offset(0).dicts()
    # urls = [
    #         {'url_key': 'iz.ru/736489/2018-04-25/gibdd-poprosila-peredat-ei-kontrol-za-tekhosmotrom-avtobusov',
    #          'id': 141080}
    #          ]
    for u in urls:


        c = Content.select(Content.url_key, Content.id).where(Content.url_key == u['url_key'], Content.id != u['id']).dicts()

        if len(c) > 0:

            if u['url_key'] not in ulrs_saved:

                print(u['url_key'].strip(), u['id'])
                # print(len(c))
                # print([e for e in c])

                ulrs_saved.append(u['url_key'])

                query = Content.delete().where(Content.url_key == u['url_key'], Content.id != u['id'])
                query.execute()

            else:
                print(u['url_key'],u['id'], 'saved before')

if __name__ == '__main__':
    run()
