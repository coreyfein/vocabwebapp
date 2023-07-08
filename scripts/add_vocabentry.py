from simplevocab.models import Word, VocabEntry
import sys
import json
import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()

def run(word_input, discovery_source_input, discovery_context_input, user, definition_override=None, synonyms_override=None, examples_override=None, etymology_override=None):    
    # lemma = get_lemma_for_word(word_input) #OED version only
    # w, created = Word.objects.get_or_create(word__iexact=lemma) #OED version only
    w, created = Word.objects.get_or_create(word__iexact=word_input)
    print(f"word id: {str(w.id)}")
    print(f"Created: {created}")
    if created:
        # word, definition_string, synonyms_string, examples_string, etymology = get_dictionary_data(lemma) #OED version
        word, definition_string, synonyms_string, examples_string, etymology = get_webster_dictionary_data(word_input)
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
    return word_found_in_dictionary, vocab_entry_already_existed_for_word

def get_or_create_vocabentry(w, discovery_source_input, discovery_context_input, user, word_freshly_created, definition_override=None, synonyms_override=None, examples_override=None, etymology_override=None):
    if word_freshly_created:
        v = VocabEntry.objects.create(
            word=w,
            discovery_source=discovery_source_input,
            discovery_context=discovery_source_input,
            user=user
        )
        vocab_entry_already_existed_for_word = False
        # .create() saves
    else:
        v, vocab_entry_created = VocabEntry.objects.get_or_create(word=w)
        if vocab_entry_created:
            v.user = user
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
        return None, vocab_entry_already_existed_for_word

    


# def get_lemma_for_word(word):
    # lemma = word # just passing it through for now, until OED API is working
    # oed_base_url = 'https://od-api.oxforddictionaries.com/api/v2'
    # OED_APPLICATION_ID = os.getenv('OED_APPLICATION_ID')
    # OED_APPLICATION_KEY = os.getenv('OED_APPLICATION_KEY')
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
    # return lemma

# def get_dictionary_data(word):
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

    # definition_string = "script def"
    # synonyms_string = "script synonyms"
    # examples_string = "script examples"
    # etymology = "script etymology"

    # dictionary_data = (word, definition_string, synonyms_string, examples_string, etymology)
    # return dictionary_data

def get_webster_dictionary_data(word):
    MERRIAM_WEBSTER_DICTIONARY_KEY = os.getenv("MERRIAM_WEBSTER_DICTIONARY_KEY")
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MERRIAM_WEBSTER_DICTIONARY_KEY}"
    response = requests.get(url)
    response_content_str = response.content.decode()
    response_content_list = json.loads(response_content_str)
    print(json.dumps(response_content_list, indent=4))
    word_dict = response_content_list[0]
    if isinstance(word_dict, str):
        dictionary_data = (word, "", "", "", "")
        return dictionary_data
    word = word_dict["meta"]["id"].split(":")[0]
    part_of_speech = word_dict["fl"]
    senses = word_dict["def"][0]["sseq"]
    definitions = []
    definition_string = ""
    examples = []
    examples_string = ""
    print(len(senses))
    for sense_count, sense in enumerate(senses):
        for sub_sense in sense:
            print("sub_sense[0]:")
            print(sub_sense[0])
            if sub_sense[0] == "sense":
                sense_dict = sub_sense[1]
            elif sub_sense[0] == "bs":
                sense_dict = sub_sense[1]["sense"]
            elif sub_sense[0] == "pseq":
                continue
            definition_list = sense_dict["dt"]
            for component in definition_list:
                if component[0] == "text":
                    definition = re.sub(r'{.+?}', '', component[1])# the regex replaces all text between consecutive { and } (and the braces themselves) with an empty string
                    if len(definitions) <= 5:
                        definitions.append(definition)
                if component[0] == "vis":
                    for example_dict in component[1]:
                        example = re.sub(r'{.+?}', '', example_dict["t"])# the regex replaces all text between consecutive { and } (and the braces themselves) with an empty string
                        examples.append(example)
    examples_string = "; ".join(examples)
    definition_string = "; ".join(definitions)
    definition_string = f'({part_of_speech}) {definition_string}'
    synonyms_string = ""
    syns = word_dict.get("syns")
    if not syns:
        # print("No synonyms found")
        pass
    else:
        synonyms_list = syns[0]["pt"][0]
    
        for count, component in enumerate(synonyms_list):
            if component == "text":
                synonyms_string = synonyms_list[count + 1].replace("{/sc} {sc}", ", ").replace("{/sc}", "")
                synonyms_string = re.sub(r'{.+?}', '', synonyms_string)# the regex replaces all text between consecutive { and } (and the braces themselves) with an empty string
    etymology = ""
    etymology_list = word_dict.get("et", [])
    for component in etymology_list:
        if component[0] == "text":
            etymology = re.sub(r'{.+?}', '', component[1])# the regex replaces all text between consecutive { and } (and the braces themselves) with an empty string
    dictionary_data = (word, definition_string, synonyms_string, examples_string, etymology)
    print(dictionary_data)
    return dictionary_data
    
    

if __name__ == "__main__":
    run()