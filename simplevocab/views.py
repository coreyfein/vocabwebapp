from simplevocab.models import Word
from simplevocab.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView


class WordListView(OwnerListView):
    model = Word
    # By convention:
    # template_name = "simplevocab/words_list.html"


class WordDetailView(OwnerDetailView):
    model = Word

class WordCreateView(OwnerCreateView):
    model = Word
    # List the fields to copy from the Words model to the Word form
    fields = ['word', 'definition', 'synonyms', 'examples', 'etymology']

class WordUpdateView(OwnerUpdateView):
    model = Word
    fields = ['word', 'definition', 'synonyms', 'examples', 'etymology']
    # This would make more sense
    # fields_exclude = ['owner', 'created_at', 'updated_at']

class WordDeleteView(OwnerDeleteView):
    model = Word