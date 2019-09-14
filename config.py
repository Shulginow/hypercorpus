source_domains = ['government.ru', 'sledcom.ru', 'mid.ru',  'cbr.ru', 'gks.ru',
'kremlin.ru', 'interfax.ru', 'novayagazeta.ru', 'rbc.ru',  'sport.rbc.ru',
'tass.ru', 'vedomosti.ru', 'tvrain.ru', 'izvestia.ru','iz.ru',  'ria.ru',
'pikabu.ru', 'kommersant.ru']

skip_pages_queque = '[^>]+(@|\/tag\/|\.ru\/images\/|author|im[0-9]\.|comments|\
issues|video|sujet|multimedia|theme|\.ru\/photo|\/edits\/)[^>]+'


ua= [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 YaBrowser/18.10.2.172 Yowser/2.5 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'
]

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'ru,en;q=0.9,uk;q=0.8,hr;q=0.7,la;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Keep-Alive': '300',
    'DNT': '1',
    'Referer': 'https://www.vl.ru',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ua[3]
}
