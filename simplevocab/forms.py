from django import forms
from simplevocab.models import Word, VocabEntry
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class VocabEntryUserInputForm(forms.Form):
    word = forms.CharField(min_length = 1, max_length=Word._meta.get_field("word").max_length)
    discovery_source = forms.CharField(
        min_length = 1, max_length=VocabEntry._meta.get_field("discovery_source").max_length
        )
    discovery_context = forms.CharField(
        min_length = 1, max_length=VocabEntry._meta.get_field("discovery_context").max_length,
        required=False
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

