from django.urls import path, reverse_lazy
from . import views

app_name='simplevocab'
urlpatterns = [
    path('', views.WordListView.as_view(), name='all'),
    path('word/<int:pk>', views.WordDetailView.as_view(), name='word_detail'),
    path('word/create',
        views.WordCreateView.as_view(success_url=reverse_lazy('simplevocab:all')), name='word_create'),
    path('word/<int:pk>/update',
        views.WordUpdateView.as_view(success_url=reverse_lazy('simplevocab:all')), name='word_update'),
    path('word/<int:pk>/delete',
        views.WordDeleteView.as_view(success_url=reverse_lazy('simplevocab:all')), name='word_delete'),
]

# We use reverse_lazy in urls.py to delay looking up the view until all the paths are defined