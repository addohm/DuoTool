from django import forms
from pprint import pprint

class TestForm(forms.Form):
    """
    Student test form
    """    
    def __init__(self, testdict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testdict = {} if testdict is None else testdict

    def dict_verify(self):
        d = self.testdict
        print('The dictionary supplied has a length of: ' + str(len(d)))
        for word in d:
            # print the base key
            answer = word
            for key in d[word]:
                value = str(d[word][key])
                if key == 'id':
                    field_name = value
                if key == 'definition':
                    question = value
                # Print the 2nd level key and value pair
                pprint(key + ': ' + str(d[word][key]))
            self.fields[field_name] = forms.CharField(label=question, max_length=100)
        