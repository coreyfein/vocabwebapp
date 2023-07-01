from django.urls import path, reverse_lazy
from . import views

app_name='simplevocab'
urlpatterns = [
    # path('words', views.WordListView.as_view(), name='all_words'),
    # path('word/<int:pk>', views.WordDetailView.as_view(), name='word_detail'),
    # path('word/create',
    #     views.WordCreateView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_create'),
    # path('word/<int:pk>/update',
    #     views.WordUpdateView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_update'),
    # path('word/<int:pk>/delete',
    #     views.WordDeleteView.as_view(success_url=reverse_lazy('simplevocab:all_words')), name='word_delete'),
    path('vocabentries', views.VocabEntryListView.as_view(), name='all_vocabentries'),
    path('vocabentry/<int:pk>',
        views.VocabEntryDetailView.as_view(), name='vocabentry_detail'),
    path('vocabentry/<int:pk>/update',
        views.VocabEntryUpdateView.as_view(), name='vocabentry_update'),#success_url set in view to vocabentry_detail for the pk
    path('vocabentry/<int:pk>/delete',
        views.VocabEntryDeleteView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocabentry_delete'),
    path('vocabentry/create',
        views.VocabEntryCreateView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocabentry_create'),
    path('upload',
        views.VocabListUploadView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='vocab_list_upload'),
    path('quiz',
        views.QuizSubmitView.as_view(success_url=reverse_lazy('simplevocab:all_vocabentries')), name='quiz'),    
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined