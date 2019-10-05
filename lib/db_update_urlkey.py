import sys
sys.path.insert(0, '..')
from models import *
from helper_html import HtmlProcess

helper_html = HtmlProcess()

def run():

    urls = Content.select(Content.url).where(Content.hrefs != 'not_set').dicts()
    for u in urls:

        url_find = u['url']
        url_key = helper_html.clean_http(url_find)
        query = Content.update(url_key=url_key).where(Content.url == url_find)
        query.execute()
        print(url_key)

if __name__ == '__main__':
    run()
