from django import forms
from .models import DuolingoUsers

class EnterUserForm(forms.ModelForm):
    class Meta:
        model = DuolingoUsers
        fields = ['username']
