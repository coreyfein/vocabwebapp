from django import forms
from simplevocab.models import Word, VocabEntry

class VocabEntryUserInputForm(forms.Form):
    word = forms.CharField(min_length = 1, max_length=Word._meta.get_field("word").max_length)
    discovery_source = forms.CharField(min_length = 1, max_length=VocabEntry._meta.get_field("discovery_source").max_length)