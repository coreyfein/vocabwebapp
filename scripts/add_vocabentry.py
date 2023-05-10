from simplevocab.models import Word, VocabEntry
import sys
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def run(word_input, discovery_source_input, user):    
    lemma = get_lemma_for_word(word_input)
    w, created = Word.objects.get_or_create(word__iexact=lemma)
    print("word id: " + str(w.id))
    print("Created: {}".format(created))
    if created:
        word, definition_string, synonyms_string, examples_string, etymology = get_dictionary_data(lemma)
        # when triggered by a form, also pass in user to the created_by field in new Word record
        w.created_by = user
        w.word = word
        w.definition = definition_string
        w.synonyms = synonyms_string
        w.examples = examples_string
        w.etymology = etymology
        w.save()
    # when triggered by a form, also pass in user to the user field in new VocabEntry record
    v = VocabEntry.objects.create(word=w, discovery_source=discovery_source_input, user=user)

def get_lemma_for_word(word):
    lemma = word # just passing it through for now, until OED API is working
    # oed_base_url = 'https://od-api.oxforddictionaries.com/api/v2'
    # OED_APPLICATION_ID = os.environ['OED_APPLICATION_ID']
    # OED_APPLICATION_KEY = os.environ['OED_APPLICATION_KEY']
    # headers = {'app_id':OED_APPLICATION_ID, 'app_key':OED_APPLICATION_KEY}
    # lemmas_url = '{}/lemmas/en/{}'.format(oed_base_url, word.lower())
    # lemmas_response = requests.get(lemmas_url, headers=headers)
    # print(lemmas_response)
    # lemmas_response_json = lemmas_response.json()
    
    # try:
    #     print(lemmas_response_json['error'])
    #     sys.exit()
    # except:
    #     pass
    
    # # a lemma is the root word with an entry in the dictionary
    # # below just gets the first lemma entry, so for words like 'learned' with two possible root words / lemmas, 
    # # the actual lemma entered will be 'learn' (the first lemma entry)
    # lemma = lemmas_response_json['results'][0]['lexicalEntries'][0]['inflectionOf'][0]['id']
    return lemma

def get_dictionary_data(word):
    # oed_base_url = 'https://od-api.oxforddictionaries.com/api/v2'
    # headers = {'app_id':OED_APPLICATION_ID, 'app_key':OED_APPLICATION_KEY}
    # entries_url = '{}/entries/en/{}'.format(oed_base_url, word.lower())
    # entries_response = requests.get(entries_url, headers=headers)
    # entries_response_json = entries_response.json()
    # first_lexical_entry = entries_response_json['results'][0]['lexicalEntries'][0]
    
    # try:
    #     etymology = first_lexical_entry['entries'][0]['etymologies'][0]
    # except:
    #     etymology = 'Etymology not found.'
    # try:
    #     first_entry_senses = first_lexical_entry['entries'][0]['senses']
    # except:
    #     print('No senses found. Exiting.')
    #     sys.exit()
    # try:
    #     first_entry_first_sense_first_definition = first_entry_senses[0]['definitions'][0]
    # except:
    #     print('No definitions found. Exiting')
    #     sys.exit()
    # try:
    #     part_of_speech = first_lexical_entry['lexicalCategory']['id']
    #     definition_string = '({}) {}'.format(part_of_speech, first_entry_first_sense_first_definition)
    # except:
    #     part_of_speech = 'Part of speech not found.'
    #     definition_string = first_entry_first_sense_first_definition
    # try:        
    #     first_entry_first_sense_synonyms = first_entry_senses[0]['synonyms']
    #     synonyms = []
    #     for synonym in first_entry_first_sense_synonyms:
    #         synonyms.append(synonym['text'])
    #     synonyms_string = ', '.join(map(str,synonyms))
    # except:
    #     synonyms_string = 'No synonyms found.'
    # try:        
    #     first_entry_first_sense_examples = first_entry_senses[0]['examples']
    #     examples = []
    #     for example in first_entry_first_sense_examples:
    #         examples.append('"{}"'.format(example['text']))
    #     examples_string = '; '.join(map(str,examples))
    # except:
    #     examples_string = 'No examples found.'
    
    # try:
    #     print(entries_response_json['error'])
    #     sys.exit()
    # except:
    #     pass
 
    # # hardcoded section for testing
    # # word = 'tyro'
    # # part_of_speech = 'noun'
    # # definition = 'a beginner in learning'
    # # definition_string = '({}) {}'.format(part_of_speech, definition)
    # # synonyms_string = 'abecedarian, apprentice, babe, beginner, colt, cub, fledgling, freshman, greenhorn, neophyte, newbie, newcomer, novice, novitiate, punk, recruit, rook, rookie, tenderfoot, virgin'
    # # examples_string = 'Most of the people in the class were tyros like me.; he\'s a good musician, but at 14, he\'s still a tyro and has a lot to learn'
    # # etymology = 'late Middle English: from Latin tiro, medieval Latin tyro "recruit"'

    definition_string = "script def"
    synonyms_string = "script synonyms"
    examples_string = "script examples"
    etymology = "script etymology"

    dictionary_data = (word, definition_string, synonyms_string, examples_string, etymology)
    return dictionary_data

if __name__ == "__main__":
    run()