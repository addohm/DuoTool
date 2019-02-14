import django
from django import forms

class TestForm(forms.Form):
    def __init__(self, testdict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.testdict = {} if testdict is None else testdict

    def dict_verify(self):
        d = self.testdict
        for word in d:
            for e, f in d[word]:
                print(f)
            #word_1 = forms.CharField(label='1', max_length=100)


