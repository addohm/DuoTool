# To do:
#     scrape cedict to check last update version
#     if current version < last update version
#     download the new version's archive
#     unzip the archive
#     parse the archive
#     move the parsed archive file into the fixtures folder
#     clear out the current Phrases database
#     write in the new phrases
# Django loaddata Source: https://docs.djangoproject.com/en/2.1/howto/initial-data/
# Dictionary Source: https://www.mdbg.net/chinese/dictionary?page=cc-cedict
# Char codes Source: http://www.math.nus.edu.sg/aslaksen/read.shtml

import json
import xml
from pprint import pprint

class Cedict(object):
    def __init__(self):
        self.dict_items = []
        self.output_directory = 'dictionaries/'
        self.output_path = ''
        self.tones = {}

    def write_json(self):
        return self._json_write()

    def write_js(self):
        new_file = open(self.output_path, "w")

        new_file.write("var CH_DIC = function() {")
        new_file.write("\n\n")
        new_file.write("\tthis._table = {")
        new_file.write("\n\n")

        for item in self.dict_items:
            try:
                new_file.write("\t\t")
                new_file.write('"' + item["simplified"] + '":')
                new_file.write(' "' + item["pinyin"] + "|" + item["definition"] + '",')
                new_file.write("\n")
            except:
                print("Something went wrong")

        new_file.write("\n")
        new_file.write("\t}")
        new_file.write("\n\n")
        new_file.write("}")

        new_file.close()
        return self.output_path

    def write_django_fixture_yaml(self, model):
        pk = 1
        with open(self.output_path, "w") as f:
            for item in self.dict_items:
                f.write('- model: ' + model + '\n')
                f.write('  pk: ' + str(pk) + '\n')
                f.write('  fields:' + '\n')
                for items in item:
                    string = []
                    string.append('    ' + str(items) + ': ')
                    string.append(str(item.get(items, '')))
                    string.append('\n')
                    f.write(' '.join(string))
                pk += 1
        f.close()

        return self.output_path

    def _json_write(self):
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.dict_items, f, indent=2, ensure_ascii=False)
        f.close()
        return self.output_path

    def write_django_fixture_json(self, model):
        new_dict = []
        pk = 1

        for item in self.dict_items:
            dict_item = {}
            dict_item['model'] = model
            dict_item['pk'] = pk
            dict_item['fields'] = item
            new_dict.append(dict_item)
            pk += 1
            
        self.dict_items = new_dict
        self._json_write()

    def convert_cedict(self, file_type, output_filename, convert, char_type='utf-8', model=None):
        # EXAMPLE INPUT LINE:   㐖 㐖 [Ye4] /see
        # TRADITIONAL_HANZI SIMPLIFIED_HANZI [PINYIN] /TRANSLATION

        with open("resources/cedict_ts.u8", "r", encoding='utf-8') as f:
            lines = f.readlines()
        f.close()

        for line in lines:
            l = line

            # These are info lines at the beginning of the file
            # NOTE: Might be useful to store version #, date, etc for dictionary reference
            if l.startswith(("#", "#!")):
                continue
            else:
                # partition out definition text, replace slshes with semicolons, normalize quotations, get rid of any \n
                defi = l.partition("/")[2].replace("/", "; ").replace('"', "'").strip()
                # Get trad and simpl hanzis then split and take only the simplified
                trad = l.partition("[")[0].split(" ", 1)[0].strip(" ")
                simp = l.partition("[")[0].split(" ", 1)[1].strip(" ")
                # Take the content in between the two brackets
                pin = l.partition("[")[2].partition("]")[0]
                
                if convert:
                    if char_type == 'ascii':
                        self.tones = TONES_ASCII
                    else:
                        self.tones = TONES_UNICODE
                    pin = self.convert_char(pin)

                self.dict_items.append({"traditional": trad, "simplified": simp, "pinyin": pin, "definition": defi})

        self.output_path = self.output_directory + output_filename

        if file_type == 'js' or file_type == 'javascript':
            self.write_js()
        if file_type == 'json':
            self.write_json()
        if file_type == 'xml':
            pass
        if model:
            if file_type == 'yaml':
                self.write_django_fixture_yaml(model)
            if file_type == 'django':
                self.write_django_fixture_json(model)

    def convert_char(self, s):
        # using v for the umlauded u
            
        word_list = []
        ret_string = ""
        tmp = ""
        # split the string by spaces
        words = s.split(" ")

        # "zhong1 guo2" -> [ ['1', 'zhong'], ['2', 'guo'] ]
        for word in words:
            word_list.append([word[len(word) - 1], word[0 : len(word) - 1]])

            # do the searchy stuff
        for word in word_list:
            tone = word[0]
            pinyin = word[1].lower()

            if tone == "5" or pinyin == "":
                break

            if pinyin.find("a") > -1:
                tmp = pinyin.replace("a", self.tones[tone + "a"])

            elif pinyin.find("e") > -1:
                tmp = pinyin.replace("e", self.tones[tone + "e"])

            elif pinyin.find("ou") > -1:
                tmp = pinyin.replace("o", self.tones[tone + "o"] + "u")

            elif pinyin.find("io") > -1:
                tmp = pinyin.replace("io", "i" + self.tones[tone + "o"])

            elif pinyin.find("iu") > -1:
                tmp = pinyin.replace("iu", "i" + self.tones[tone + "u"])

            elif pinyin.find("ui") > -1:
                tmp = pinyin.replace("ui", "u" + self.tones[tone + "i"])

            elif pinyin.find("uo") > -1:
                tmp = pinyin.replace("uo", "u" + self.tones[tone + "o"])

            elif pinyin.find("i") > -1:
                tmp = pinyin.replace("i", self.tones[tone + "i"])

            elif pinyin.find("o") > -1:
                tmp = pinyin.replace("o", self.tones[tone + "o"])

            elif pinyin.find("u:") > -1:
                tmp = pinyin.replace("u:", self.tones[tone + "v"])

            elif pinyin.find("u") > -1:
                tmp = pinyin.replace("u", self.tones[tone + "u"])

            else:
                tmp = pinyin

            ret_string += tmp + " "

        return ret_string
        

TONES_UNICODE = {
    "1a": chr(257),
    "2a": chr(225),
    "3a": chr(462),
    "4a": chr(224),
    "1e": chr(275),
    "2e": chr(233),
    "3e": chr(283),
    "4e": chr(232),
    "1i": chr(299),
    "2i": chr(237),
    "3i": chr(464),
    "4i": chr(236),
    "1o": chr(333),
    "2o": chr(243),
    "3o": chr(466),
    "4o": chr(242),
    "1u": chr(363),
    "2u": chr(250),
    "3u": chr(468),
    "4u": chr(249),
    "1v": chr(470),
    "2v": chr(472),
    "3v": chr(474),
    "4v": chr(476),
}

TONES_ASCII = {
    "1a": "&#257;",
    "2a": "&#225;",
    "3a": "&#462;",
    "4a": "&#224;",
    "1e": "&#275;",
    "2e": "&#233;",
    "3e": "&#283;",
    "4e": "&#232;",
    "1i": "&#299;",
    "2i": "&#237;",
    "3i": "&#464;",
    "4i": "&#236;",
    "1o": "&#333;",
    "2o": "&#243;",
    "3o": "&#466;",
    "4o": "&#242",
    "1u": "&#363;",
    "2u": "&#250;",
    "3u": "&#468;",
    "4u": "&#249;",
    "1v": "&#470;",
    "2v": "&#472;",
    "3v": "&#474;",
    "4v": "&#476;",
}

if __name__ == '__main__':
    from pprint import pprint
    c = Cedict()
    # c.convert_cedict('django', 'main.json', convert=True, model='main.Phrases')
    # c.convert_cedict('yaml', 'main.yaml', convert=True, model='main.Phrases')
    # c.convert_cedict('json', 'cedict.json', convert=False)
    # c.convert_cedict('js', 'cedict.js', convert=False)
