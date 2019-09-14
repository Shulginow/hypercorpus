
def get_filter_fields():

    pos_options = [
        ('Все', 'pos_all'),
        ('Существительные', 'pos_NOUN'),
        ('Глаголы', 'pos_VERB'),
        ('Прилагательные', 'pos_ADJ')
    ]

    count_options = [
        ('Любое', 'count_all'),
        (1, 'count_1'),
        (2, 'count_2'),
        (3, 'count_3'),
        ('Более 3', 'count_100')
    ]

    syntax_options = [
        ('Все', 'syntax_all'),
        ('Ссылка содержит root', 'syntax_linkroot'),
        ('Ссылка не содержит root', 'syntax_linknoroot')
    ]

    return pos_options, count_options, syntax_options
