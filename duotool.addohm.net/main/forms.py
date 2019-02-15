from django import forms
import os
from django.conf import settings
import json
from pprint import pprint

class TestForm(forms.Form):
    """
    Student test form
    """    
    def __init__(self, test_dict=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resource_path = os.path.join(settings.BASE_DIR, 'static/json')
        self._json_path = os.path.join(self._resource_path, 'answers.json')
        i = 0
        if test_dict is not None:
            self.test_dict = test_dict
            # Save the test_dict
            print('Saving the test dictionary')
            with open(self._json_path, 'w', encoding='utf-8') as f:
                json.dump(test_dict, f, indent=2, ensure_ascii=False)
            answer, wordid, question = self._unpack_dict(test_dict)
        else:
            # Open the test_dict
            print('Reading the test dictionary')
            with open(self._json_path, 'r', encoding='utf-8') as json_data:
                test_dict = json.load(json_data)
                json_data.close()
            self.test_dict = test_dict
            answer, wordid, question = self._unpack_dict(test_dict)
        for i in range(len(question)):
            field_name = 'testword' + wordid[i]
            print(str(i))
            print('id: ' + str(wordid[i]))
            print('question: ' + question[i])
            print('answer:' + answer[i])
            self.fields[field_name] = forms.CharField(label=question[i], max_length=100)
        self.question = question
        self.wordid = wordid      
        self.answer = answer

    def clean(self):
        print('CLEANING DATA')
        context = {}
        i = 0
        # Open the test_dict
        with open(self._json_path, 'r', encoding='utf-8') as json_data:
            test_dict = json.load(json_data)
            json_data.close()
        answer, wordid, question = self._unpack_dict(test_dict)
        # Get and check the results
        for i in range(len(self.cleaned_data)):
            field_name = 'testword' + wordid[i]
            pprint(field_name)
            result = self.cleaned_data.get(field_name)
            pprint('Result is: ' + result)
            pprint('Answers are: ' + str(answer))
            if result != answer[i]:
                self.add_error(field_name, 'Incorrect')
            context[i] = question[i]
            i += 1
        return context

    def _unpack_dict(self, test_dict):
        answer = []
        wordid = []
        question = []
        d = test_dict
        for word in d:
            answer.append(word)
            for key in d[word]:
                value = str(d[word][key])
                if key == 'id':
                    wordid.append(value)
                if key == 'definition':
                    question.append(value)
        return answer, wordid, question
