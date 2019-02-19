import os
import json
from django.conf import settings
from django import forms
from .models import TestAnswers
from pprint import pprint

class TestForm(forms.Form):
    """
    Student test form
    """    
    def __init__(self, test_dict=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resource_path = os.path.join(settings.BASE_DIR, 'static/json')
        self._json_path = os.path.join(self._resource_path, 'answers.json')
        self._model = TestAnswers
        i = 0
        phraseid, answer, question = [], [], []
        if test_dict is not None:
        # A form get request should resolve new form data and
        # store it in the database for comparison later on
            # clear out the answers table
            self._model.objects.all().delete()
            # create a list of model objects to bulk insert
            records = []
            for item in test_dict:
                record = self._model(
                    phraseid=test_dict[item]['id'],
                    answer=item,
                    question=test_dict[item]['definition']
                )
                phraseid.append(test_dict[item]['id'])
                question.append(test_dict[item]['definition'])
                answer.append(item)
                records.append(record)
            if records:
                # Insert the records into the TestAnswers table
                self._model.objects.bulk_create(records)
            self.test_dict = test_dict

        else:
        # A form post request should check the form data against
        # what was established during the get request
            # Get all the objects in the test table
            records = self._model.objects.all()
            # Put all the object items into their respective lists
            for r in records:
                phraseid.append(r.phraseid)
                answer.append(r.answer)
                question.append(r.question)
        for i in range(len(question)):
            # Set the form fields
            field_name = 'testword' + str(phraseid[i])
            # Print the answers for debugging
            print('id: ' + str(phraseid[i]))
            print('question: ' + question[i])
            print('answer:' + answer[i])
            self.fields[field_name] = forms.CharField(label=question[i], max_length=100)
        self.question = question
        self.phraseid = phraseid
        self.answer = answer

    def clean(self):
        # print('CLEANING DATA')
        phraseid, answer, question = [], [], []
        context = {}
        i = 0
        records = self._model.objects.all()
        for r in records:
            phraseid.append(r.phraseid)
            answer.append(r.answer)
            question.append(r.question)
        # Get and check the results
        for i in range(len(self.cleaned_data)):
            field_name = 'testword' + str(phraseid[i])
            result = self.cleaned_data.get(field_name)
            if result != answer[i]:
                self.add_error(field_name, 'Incorrect')
            context[i] = question[i]
            i += 1
        return context

    def _unpack_dict(self, test_dict):
        answer = []
        phraseid = []
        question = []
        d = test_dict
        for word in d:
            answer.append(word)
            for key in d[word]:
                value = str(d[word][key])
                if key == 'id':
                    phraseid.append(value)
                if key == 'definition':
                    question.append(value)
        return answer, phraseid, question


class HskLevelSelectForm(forms.Form):
    level = forms.ChoiceField(choices=[(x, x) for x in range(1, 7)])
