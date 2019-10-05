import sys
sys.path.insert(0, '..')
from models import *

def run():
    keys_saved = []
    keys = LinkStat.raw("""
            SELECT DISTINCT
                document_url,source_url,link_text, CONCAT(document_url,source_url,link_text) as id_key, id
            FROM link_stat
            """).dicts()


    for u in keys:

        try:
            q = """
                SELECT DISTINCT
                    document_url,source_url,link_text, CONCAT(document_url,source_url,link_text) as id_key, id
                FROM link_stat
                WHERE document_url = '{}' and source_url = '{}' and link_text  = '{}' and id != '{}'
                """.format(u['document_url'], u['source_url'], u['link_text'], u['id'])
            # print(q)
            c = LinkStat.raw(q).dicts()

            #c = LinkStat.select(LinkStat.url_key, LinkStat.id).where(LinkStat.url_key == u['url_key'], LinkStat.id != u['id']).dicts()
            if len(c) > 0:
                if u['id_key'] not in keys_saved:
                    print(u['id_key'].strip(), u['id'])
                    # print(len(c))
                    # print([e for e in c])

                    keys_saved.append(u['id_key'])
                    # q = """
                    #     DELETE FROM link_stat
                    #     WHERE document_url = '{}' and source_url = '{}' and link_text  = '{}' and id != '{}'
                    #     """.format(u['document_url'], u['source_url'], u['link_text'], u['id'])
                    # d_query = LinkStat.raw(q)
                    d_query = LinkStat.delete().where(LinkStat.document_url == u['document_url'], LinkStat.source_url == u['source_url'], LinkStat.link_text == u['link_text'], LinkStat.id != u['id'])
                    d_query.execute()

                else:
                    print(u['id_key'],u['id'], 'saved before')
        except Exception as e:
            print(e, q)

if __name__ == '__main__':
    run()
