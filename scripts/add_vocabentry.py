from simplevocab.models import Word, VocabEntry
from scripts import build_dictionary_data

def run(word_input, discovery_source_input, discovery_context_input, user, definition_override=None, synonyms_override=None, examples_override=None, etymology_override=None):    
    # lemma = get_lemma_for_word(word_input) #OED version only
    # w, created = Word.objects.get_or_create(word__iexact=lemma) #OED version only
    discovery_source_input = discovery_source_input.strip()
    discovery_context_input = discovery_context_input.strip()
    w, created = Word.objects.get_or_create(word__iexact=word_input)
    print(f"word id: {str(w.id)}")
    print(f"Created: {created}")
    if created:
        # word, definition_string, synonyms_string, examples_string, etymology = get_oed_dictionary_data(lemma)
        word, definition_string, synonyms_string, examples_string, etymology = build_dictionary_data.run(word_input)
        # when triggered by a form, also pass in user to the created_by field in new Word record
        w.created_by = user
        w.word = word
        w.definition = definition_string
        w.synonyms = synonyms_string
        w.examples = examples_string
        w.etymology = etymology
        w.save()
        if definition_string == "":# word is set to an empty string if not found in the dictionary
            word_found_in_dictionary = False #this is just for returning success variable later, it's okay that we added the word above anyway.
        else:
            word_found_in_dictionary = True
    else:
        word_found_in_dictionary = True# in this case, word was found in Word table
    v, vocab_entry_already_existed_for_word = get_or_create_vocabentry(w, discovery_source_input, discovery_context_input, user, created, definition_override, synonyms_override, examples_override, etymology_override)
    
    print(f"vocab_entry_already_existed_for_word: {vocab_entry_already_existed_for_word}")
    print(f"word_found_in_dictionary: {word_found_in_dictionary}")
    return v.id, word_found_in_dictionary, vocab_entry_already_existed_for_word

def get_or_create_vocabentry(w, discovery_source_input, discovery_context_input, user, word_freshly_created, definition_override=None, synonyms_override=None, examples_override=None, etymology_override=None):
    if word_freshly_created:
        v = VocabEntry.objects.create(
            word=w,
            discovery_source=discovery_source_input,
            discovery_context=discovery_context_input,
            user=user
        )
        vocab_entry_already_existed_for_word = False
        # .create() saves
    else:
        v, vocab_entry_created = VocabEntry.objects.get_or_create(word=w, user=user)
        if vocab_entry_created:
            v.discovery_source = discovery_source_input
            vocab_entry_already_existed_for_word = False
        else:
            vocab_entry_already_existed_for_word = True
    
    if not vocab_entry_already_existed_for_word:
        if definition_override:
            v.definition_override = definition_override
        if synonyms_override:
            v.synonyms_override = synonyms_override
        if examples_override:
            v.examples_override = examples_override
        if etymology_override:
            v.etymology_override = etymology_override
        if discovery_context_input:
            v.discovery_context = discovery_context_input
        v.save()
        return v, vocab_entry_already_existed_for_word
    
    else:
        return v, vocab_entry_already_existed_for_word
    
if __name__ == "__main__":
    run()    