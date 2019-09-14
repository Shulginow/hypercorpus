import texterra
import json

class SyntaxParser:

    def __init__(self):

        keys = [
                '639119f7f746bb811e85a8ba6249904b4783d0f9',
                '726175a5ddd50fe8e60b5e454513c0732013f82a',
                '43cd53787c21715fdf17dbc46f7efd314ed7e19f'
        ]
        self.texterra_keys_q = len(keys)
        self.texterra_apis = [texterra.API(key) for key in keys]
        self.texterra_api = texterra.API('639119f7f746bb811e85a8ba6249904b4783d0f9')
        # self.texterra_api = texterra.API('726175a5ddd50fe8e60b5e454513c0732013f82a')

    def define_named_entities(self, text):
        """Распознавание именованных сущностей"""
        r = []
        tags = self.texterra_api.named_entities(text)

        for i in tags:
            r.append(i)

        return r


    def define_syntax_tree(self, text, api_num = 0):
        """Построение синтаксического дерева"""

        tags = self.texterra_apis[api_num].syntax_detection(text)
        tree = []
        for tag in tags:
            element = tag.tree
            #print(element)
            #print('-----')
            element_str = self.list_keys_to_string([element])
            tree.append(element_str)

        jtree = json.dumps(tree)

        return jtree


    def define_syntax_tags(self, text):
        """вывод тегов"""

        tags = self.texterra_api.syntax_detection(text)
        x = [i.get_labels() for i in tags]

        return x


    def define_syntax_tokens(self, text):
        """вывод термов и позиций"""

        tokens = self.texterra_api.tokenization(text)
        y = [i for i in tokens]

        return y


    def define_link_tag(self, text, word, start_position):
        #print(text, word, start_position)
        response = ''
        tag_txt = ''
        tags = self.define_syntax_tags(text)
        tags = tags[0]
        tokens = self.define_syntax_tokens(text)

        for index, t in enumerate(tokens[0]):
            # print(t)
            if t[2] == word:

                if abs(t[0] - start_position) < 5:
                    response, tag_txt = tags[index], t[2]
                    break

        return response, tag_txt


    def list_keys_to_string(self,list_):
        nl = []

        for d in list_:
            if isinstance(d, list):
                d = self.list_keys_to_string(list_)
                nl.append(d)
            elif isinstance(d, dict):
                nl.append(self.keys_to_string(d))
            else:
                nl.append(d)

        return nl


    def keys_to_string(self, d):
        nd = {}
        for k, v in d.items():
            nk = str(k)
            if isinstance(v, dict):
                nd[nk] = self.keys_to_string(v)
            if isinstance(v, list):
                nd[nk] = self.list_keys_to_string(v)
            else:
                nd[nk] = v

        return nd


# t1 = """Президент и основатель сети «М.Видео» Александр Тынкован заявил, что,
#     согласно условиям договора, заключенного с группой «Сафмар», он и его партнеры в течение определенного
#     времени не имеют право запускать подобные «М.Видео» бизнесы."""

# tree = SyntaxParser.define_syntax_tree(t1)
# tags = SyntaxParser.define_syntax_tags(t1)
# tokens = SyntaxParser.define_syntax_tokens(t2)
#
# # tags = texterra_api.syntax_detection(t1)
# # x = [i.get_labels() for i in tags]
#
#
#
# j = SyntaxParser.define_link_tag(t1, 'основатель', 12)
# print(j)





sp = SyntaxParser()

t2  = """Принятый документ подготовлен совместно левыми и либеральными фракциями
Европарламента и прошел первые дебаты 26 апреля."""
tree = sp.define_syntax_tree(t2)
