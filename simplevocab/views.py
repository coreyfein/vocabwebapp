from simplevocab.models import Word, VocabEntry
from simplevocab.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView
from simplevocab.forms import VocabEntryUserInputForm
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from scripts import add_vocabentry

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
    fields = ['definition_override', 'synonyms_override', 'examples_override', 'etymology_override', 'discovery_source']
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
        return initial
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        word = form.cleaned_data["word"]
        discovery_source = form.cleaned_data["discovery_source"]
        user = self.request.user
        add_vocabentry.run(word, discovery_source, user)
        return super().form_valid(form)
    
        

