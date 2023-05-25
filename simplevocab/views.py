from simplevocab.models import Word, VocabEntry
from simplevocab.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from simplevocab.forms import VocabEntryUserInputForm, VocabListUploadForm
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from scripts import add_vocabentry
import csv
from io import TextIOWrapper

class WordListView(OwnerListView):
    model = Word
    field_to_filter_by = "created_by"
    # By convention:
    # template_name = "simplevocab/words_list.html"


class WordDetailView(OwnerDetailView):
    model = Word

# WordCreateView(OwnerUpdateView) creates a word in the Word table with manually entered word data. 
# Instead, a new version should just receive a form input with word and discovery_source, 
# get_or_create a Word record, update the Word record with definitions etc. if just created,
# and create a VocabEntry record (user, discovery_source, word_id)
# Standalone script add_vocabentry basically does this, needs to be adapated to a view
class WordCreateView(OwnerCreateView):
    model = Word
    # List the fields to copy from the Words model to the Word form
    fields = ['word', 'definition', 'synonyms', 'examples', 'etymology']

class WordUpdateView(OwnerUpdateView):
    model = Word
    field_to_filter_by = "created_by"
    fields = ['word', 'definition', 'synonyms', 'examples', 'etymology']

class WordDeleteView(OwnerDeleteView):
    model = Word

class VocabEntryListView(OwnerListView):
    model = VocabEntry
    field_to_filter_by = "user"
    # By convention:
    # template_name = "simplevocab/vocabentry_list.html"

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
    
class VocabEntryDeleteView(OwnerDeleteView):
    model = VocabEntry
    field_to_filter_by = "user"

class VocabEntryCreateView(LoginRequiredMixin, FormView):
    template_name = "simplevocab/vocabentry_user_input.html"
    form_class = VocabEntryUserInputForm
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
        discovery_context = form.cleaned_data["discovery_source"]
        user = self.request.user
        add_vocabentry.run(word, discovery_source, discovery_context, user)
        return super().form_valid(form)
    
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

        for row, item in enumerate(dict_reader, start=1):
            word = item.get("word")
            discovery_source = item.get("discovery_source", "Uploaded from previous vocab list")
            discovery_context = item.get("discovery_context")
            definition_override = item.get("definition")
            synonyms_override = item.get("synonyms")
            examples_override = item.get("examples")
            etymology_override = item.get("etymology")
            add_vocabentry.run(word, discovery_source, discovery_context, user, definition_override, synonyms_override, examples_override, etymology_override)

        return super().form_valid(form)
    
        

