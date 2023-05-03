from django.contrib import admin
from simplevocab.models import Word, VocabEntry, QuizResponse

# Register your models here.

admin.site.register(Word)
admin.site.register(VocabEntry)
admin.site.register(QuizResponse)