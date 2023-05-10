from django.urls import path, reverse_lazy
from . import views

app_name='simplevocab'
urlpatterns = [
    path('words', views.WordListView.as_view(), name='all_words'),
    path('word/<int:pk>', views.WordDetailView.as_view(), name='word_detail'),
    path('word/create',
        views.WordCreateView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_create'),
    path('word/<int:pk>/update',
        views.WordUpdateView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_update'),
    path('word/<int:pk>/delete',
        views.WordDeleteView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_delete'),
    path('vocabentries', views.VocabEntryListView.as_view(), name='all_vocabentries'),
    path('vocabentry/<int:pk>/update',
        views.VocabEntryUpdateView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocabentry_update'),
    path('vocabentry/<int:pk>/delete',
        views.VocabEntryDeleteView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocabentry_delete'),
    path('vocabentry/create',
        views.VocabEntryCreateView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocabentry_create'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined