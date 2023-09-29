from simplevocab.models import Word
from scripts import build_dictionary_data

def run():    
    all_words = Word.objects.all()
    done_words = []
    for count, word in enumerate(all_words):
        print(f"Retrieving new data for word: {word.word} ({count + 1} / {len(all_words)})")
        new_word, new_definition_string, new_synonyms_string, new_examples_string, new_etymology = build_dictionary_data.run(word.word)
        word.word = new_word
        word.definition = new_definition_string
        word.synonyms = new_synonyms_string
        word.examples = new_examples_string
        word.etymology = new_etymology
        word.save()
        done_words.append(word.word)
        print(f"done_words: {done_words}")

if __name__ == "__main__":
    run()    