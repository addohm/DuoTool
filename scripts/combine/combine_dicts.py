"""
Combine the data from cedict and hanzidb to create:
    class Phrases(models.Model):
        traditional = models.CharField(max_length = 20)
        simplified = models.CharField(max_length = 20)
        radical = models.CharField(max_length = 20)
        pinyin = models.CharField(max_length = 255)
        hsk_level = models.IntegerField
        frequency_rank = models.IntegerField
        phrase_url = models.URLField
        radical_url = models.URLField
        definition = models.TextField()
"""
import sys, os
import json
from pprint import pprint

class CombineDictData(object):
    def __init__(self):
        self._root_folder_path = os.path.dirname(sys.argv[0])
        self._hanzidb_dict = {}
        self._cedict_dict = {}

    def get_hanzidb_dict(self):
        with open(os.path.join(self._root_folder_path, 'resources/hanzidb.json'), 'r', encoding='utf-8') as h:
            hanzidb_dict = json.load(h)
        h.close()
        self._hanzidb_dict = hanzidb_dict

    def get_cedict_dict(self):
        with open(os.path.join(self._root_folder_path, 'resources/cedict.json'), 'r', encoding='utf-8') as c:
            cedict_dict = json.load(c)
        c.close()
        self._cedict_dict = cedict_dict

    def _json_write(self, json_data, output_path=None):
        if output_path is None:
            output_path = self._root_folder_path + '/combined_dicts.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        f.close()
        return output_path

    def combine(self, model):
        h = self._hanzidb_dict
        c = self._cedict_dict
        new_dict = []
        pk = 1

        for item in c:
            phrase = item['simplified']
            dict_entry = {}
            dict_entry['model'] = model
            dict_entry['pk'] = pk
            if phrase in h:
                item['simplified_radical'] = h[phrase][0]['radical']
                hsklevel = h[phrase][0]['hsk_level']
                item['hsk_level'] = int(hsklevel) if hsklevel != '' and hsklevel is not None else 0
                frequency = h[phrase][0]['frequency_rank']
                item['frequency_rank'] = int(frequency) if frequency != '' and frequency is not None else 0
                item['phrase_url'] = h[phrase][0]['char_url']
                try:
                    item['radical_url'] = h[phrase][0]['radical_url']
                except:
                    item['radical_url'] = ''
            else:
                item['simplified_radical'] = ''
                item['hsk_level'] = 0
                item['frequency_rank'] = 0
                item['phrase_url'] = ''
                item['radical_url'] = ''
            dict_entry['fields'] = item
            new_dict.append(dict_entry)
            pk += 1
        return self._json_write(new_dict)

if __name__ == '__main__':
    comb = CombineDictData()
    comb.get_hanzidb_dict()
    comb.get_cedict_dict()
    comb.combine('main.Dictionary')
    pass

# def write_django_fixture_json(self, model):
#     new_dict = []
#     pk = 1

#     for item in self.dict_items:
#         dict_item = {}
#         dict_item['model'] = model
#         dict_item['pk'] = pk
#         dict_item['fields'] = item
#         new_dict.append(dict_item)
#         pk += 1
        
#     self.dict_items = new_dict
#     self._json_write()