from django import forms
from simplevocab.models import Word, VocabEntry
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class VocabEntryUserInputForm(forms.Form):
    discovery_context = forms.CharField(
        min_length = 1, 
        max_length=VocabEntry._meta.get_field("discovery_context").max_length,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    word = forms.CharField(min_length = 1, 
        max_length=Word._meta.get_field("word").max_length,
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    discovery_source = forms.CharField(
        min_length = 1, 
        max_length=VocabEntry._meta.get_field("discovery_source").max_length,
        widget=forms.TextInput(
            attrs={
                'class':'form-control'
            }
        )
    )
    

class VocabListUploadForm(forms.Form):
    file = forms.FileField()
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        if not file.name.endswith(".csv"):
            raise ValidationError(
                {
                    "file": _("Filetype not supported, the file must be a '.csv'"),
                }
            )
        return cleaned_data

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.vocabentries_to_quiz = kwargs.pop("vocabentries_to_quiz")#retrieve vocabentries_to_quiz from views.py and remove from kwargs before running __init__
        choices = [
        (1, 'Correct'),
        (0, 'Incorrect'),
        ]
        self.base_fields = {}# for some reason self.base_fields was sometimes (and only sometimes) populating with fields before this, 
        # causing extra hidden fields to be present and prevent form from being submitted. clearing it here fixed the bug.
        for vocab_entry_dict in self.vocabentries_to_quiz:
            self.base_fields["vocab_entry_{}".format(vocab_entry_dict["vocab_entry"].id)] = forms.ChoiceField(
                widget=forms.RadioSelect,
                choices=choices
            )
        super(QuizForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data