from typing import Any, Dict
from simplevocab.models import Word, VocabEntry
from simplevocab.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from simplevocab.forms import VocabEntryUserInputForm, VocabListUploadForm, QuizForm
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from scripts import add_vocabentry, create_quiz_queue, add_quizresponses, get_response_stats
import csv
from io import TextIOWrapper

@login_required
def vocab_entry_export(request):
    csv_export = HttpResponse(content_type='text/csv')
    csv_export['Content-Disposition'] = 'attachment; filename="vocab_list.csv"'
    writer = csv.writer(csv_export)
    writer.writerow(['word', 'discovery_source', 'discovery_context', 'definition', 'synonyms', 'examples', 'etymology'])
    vocab_entries = VocabEntry.objects.filter(user=request.user.id).order_by("-created_at")
    for vocab_entry in vocab_entries:
        word = vocab_entry.word.word
        if vocab_entry.definition_override and vocab_entry.definition_override != "":
            definition = vocab_entry.definition_override
        else:
            definition = vocab_entry.word.definition
        if vocab_entry.synonyms_override and vocab_entry.synonyms_override != "":
            synonyms = vocab_entry.synonyms_override
        else:
            synonyms = vocab_entry.word.synonyms
        if vocab_entry.examples_override and vocab_entry.examples_override != "":
            examples = vocab_entry.examples_override
        else:
            examples = vocab_entry.word.examples
        if vocab_entry.etymology_override and vocab_entry.etymology_override != "":
            etymology = vocab_entry.etymology_override
        else:
            etymology = vocab_entry.word.etymology
        discovery_source = vocab_entry.discovery_source
        discovery_context = vocab_entry.discovery_context
        row = [word, discovery_source, discovery_context, definition, synonyms, examples, etymology]
        writer.writerow(row)
    return csv_export

class VocabEntryListView(OwnerListView):
    model = VocabEntry
    field_to_filter_by = "user"
    # By convention:
    # template_name = "simplevocab/vocabentry_list.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response_stats = get_response_stats.run(self.request.user)
        context['response_stats'] = response_stats
        return context

class VocabEntryDetailView(OwnerDetailView):
    model = VocabEntry

class VocabEntryUpdateView(OwnerUpdateView):
    model = VocabEntry
    template_name_suffix = "_update_form"
    field_to_filter_by = "user"
    fields = ['definition_override', 'synonyms_override', 'examples_override', 'etymology_override', 'discovery_source', 'discovery_context']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vocabentry_id = self.kwargs['pk']
        vocabentry = VocabEntry.objects.get(id=vocabentry_id)
        word = vocabentry.word.word
        context['word'] = word
        return context
    
    def get_success_url(self):
        vocabentry_id = self.object.pk
        return reverse_lazy('simplevocab:vocabentry_detail', kwargs={'pk': vocabentry_id})
    
class VocabEntryDeleteView(OwnerDeleteView):
    model = VocabEntry
    field_to_filter_by = "user"

class VocabEntryCreateView(LoginRequiredMixin, FormView):
    template_name = "simplevocab/vocabentry_user_input.html"
    form_class = VocabEntryUserInputForm
    def __init__(self):
        self.vocabentry_id = None
        self.word_found_in_dictionary = None
    def get_initial(self):
        initial = super().get_initial()
        initial["word"] = self.request.GET.get("word")
        initial["discovery_source"] = self.request.GET.get("discovery_source")
        initial["discovery_context"] = self.request.GET.get("discovery_context")
        return initial
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        word = form.cleaned_data["word"]
        discovery_source = form.cleaned_data["discovery_source"]
        discovery_context = form.cleaned_data["discovery_context"]
        user = self.request.user
        vocabentry_id, word_found_in_dictionary, vocab_entry_already_existed_for_word = add_vocabentry.run(word, discovery_source, discovery_context, user)
        self.vocab_entry_id = int(vocabentry_id)
        self.word_found_in_dictionary = word_found_in_dictionary
        print(f"vocab_entry_id: {vocabentry_id}")
        return super().form_valid(form)
    def get_success_url(self):
        if self.word_found_in_dictionary:
            return reverse_lazy('simplevocab:vocabentry_detail', kwargs={'pk': self.vocab_entry_id})
        else:
            # for now, we create the word and vocabentry and don't have a message/page to notify the user that no definition was found so it will route the same way. 
            # eventually, should route to a page explaining that no definition was found
            return reverse_lazy('simplevocab:vocabentry_detail', kwargs={'pk': self.vocab_entry_id})
    
class VocabListUploadView(LoginRequiredMixin, FormView):
    template_name = "simplevocab/vocab_list_upload.html"
    form_class = VocabListUploadForm

    def form_valid(self, form):
        user = self.request.user
        csv_file = form.cleaned_data["file"]
        f = TextIOWrapper(csv_file.file)
        dict_reader = csv.DictReader(f)
        required_columns = ["word"]
        # Check needed columns exist
        for req_col in required_columns:
            if req_col not in dict_reader.fieldnames:
                raise Exception(
                    f"A required column is missing from the uploaded CSV: '{req_col}'"
                )
        words_not_found_in_dictionary = []
        words_where_vocab_entry_already_existed = []
        for row, item in enumerate(dict_reader, start=1):
            word = item.get("word")
            discovery_source = item.get("discovery_source", "Uploaded from previous vocab list")
            discovery_context = item.get("discovery_context")
            definition_override = item.get("definition")
            synonyms_override = item.get("synonyms")
            examples_override = item.get("examples")
            etymology_override = item.get("etymology")
            vocab_entry_id, word_found_in_dictionary, vocab_entry_already_existed_for_word = add_vocabentry.run(word, discovery_source, discovery_context, user, definition_override, synonyms_override, examples_override, etymology_override)
            if not word_found_in_dictionary:
                words_not_found_in_dictionary.append((word))
            if vocab_entry_already_existed_for_word:
                words_where_vocab_entry_already_existed.append(word)
        print("words_not_found_in_dictionary: {}".format(words_not_found_in_dictionary))# Show this to the user somehow (passed to some page as a message?)
        print("words_where_vocab_entry_already_existed: {}".format(words_where_vocab_entry_already_existed))# Show this to the user somehow (passed to some page as a message?)

        return super().form_valid(form)
    
class QuizSubmitView(LoginRequiredMixin, FormView):
    template_name = "simplevocab/quiz.html"
    form_class = QuizForm

    def get_form_kwargs(self):
        self.vocabentries_to_quiz = create_quiz_queue.run(self.request.user, 10)
        kwargs = super(QuizSubmitView, self).get_form_kwargs()
        kwargs.update({"vocabentries_to_quiz": self.vocabentries_to_quiz})# pass self.vocabentries_to_quiz into forms.py
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vocabentries_to_quiz"] = self.vocabentries_to_quiz
        return context
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        print(form.cleaned_data)
        q = add_quizresponses.run(form.cleaned_data, self.request.user)
        print(q)
        return super().form_valid(form)