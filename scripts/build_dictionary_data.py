from scripts import misc_helpers
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv()

def run(word):
    # Good examples for testing: monitor, feline, abaca, abeyance, absence, baloney, sown, forbode, chary
    """
    1. Call to Webster API, retrieve lemma ('id')
    - If not found, try WordsAPI (see below)
    2. In Webster API response, for each main entry:
    - webster_etymology_str. Look for 'et' -- stop after finding one.
    - Generate webster_definition_str: look for 'def'. Handle additional definition components (e.g. "ca", "sdsense" etc)
    - Generate webster_synonyms_str: look for 'syn'
    - Generate webster_examples_str: look for 'vis' within 'def' and look for 'quotes'
    - Prefix each entry with a number so that synonyms and examples visually correspond to particular a definition
    3. If Webster didn't find any synonyms or examples, try WordsAPI. For each WordsAPI "result":
    - if len(results) > 1 and retrieving Webster lemma failed, include number prefix in definition_str, synonyms_str, examples_str
    - Generate wordsapi_definition_str
    - Generate wordsapi_synonyms_str
    - Generate wordsapi_examples_str
    4. Finalize synonyms_str, examples_str
    - Use Webster for each if available, otherwise use WordsAPI (with result numbers removed since they wouldn't correspond to Webster entry numbers)
    """

    lemma, webster_top_level_list = get_webster_data(word)
    if not lemma:# word not found at Webster
        print("Word not found at Webster")
        wordsapi_data = get_wordsapi_data(word)# check word (whatever they submitted) instead of lemma, since didn't get lemma from webster
        if wordsapi_data.get("message") == "word not found" or not wordsapi_data.get("results"):# word not found at WordsAPI
            print ("Word not found at WordsAPI")
            dictionary_data = (word, "", "", "", "")
        else:
            wordsapi_definition_str, wordsapi_synonyms_str, wordsapi_examples_str = extract_wordsapi_data(wordsapi_data, exclude_synonym_result_nums=False, exclude_example_result_nums=False)
            dictionary_data = (word, wordsapi_definition_str, wordsapi_synonyms_str, wordsapi_examples_str, "")

    else:# found word at webster  
        webster_definition_str, webster_synonyms_str, webster_examples_str, webster_etymology = extract_webster_data(webster_top_level_list)
        print(f"webster_definition_str: {webster_definition_str}")
        print(f"webster_synonyms_str: {webster_synonyms_str}")
        print(f"webster_examples_str: {webster_examples_str}")
        print(f"webster_etymology: {webster_etymology}")

        exclude_synonym_result_nums = False
        exclude_example_result_nums = False
        if webster_synonyms_str == "":
            exclude_synonym_result_nums = True
        if webster_examples_str == "":
            exclude_example_result_nums = True
        
        if exclude_synonym_result_nums or exclude_example_result_nums:
            wordsapi_data = get_wordsapi_data(lemma)
            
            if wordsapi_data.get("message") == "word not found" or not wordsapi_data.get("results"):# word not found at WordsAPI
                dictionary_data = (lemma, webster_definition_str, webster_synonyms_str, webster_examples_str, webster_etymology)
            else:
                wordsapi_definition_str, wordsapi_synonyms_str, wordsapi_examples_str = extract_wordsapi_data(wordsapi_data, exclude_synonym_result_nums, exclude_example_result_nums)
                print(f"wordsapi_definition_str: {wordsapi_definition_str}")
                print(f"wordsapi_synonyms_str: {wordsapi_synonyms_str}")
                print(f"wordsapi_examples_str: {wordsapi_examples_str}")

                if exclude_synonym_result_nums:
                    synonyms_str = wordsapi_synonyms_str
                else:
                    synonyms_str = webster_synonyms_str

                if exclude_example_result_nums:
                    examples_str = wordsapi_examples_str
                else:
                    examples_str = webster_examples_str

                dictionary_data = (lemma, webster_definition_str, synonyms_str, examples_str, webster_etymology)

        else:
            dictionary_data = (lemma, webster_definition_str, webster_synonyms_str, webster_examples_str, webster_etymology)

    print("Lemma: " + dictionary_data[0])
    print("Final definition: " + dictionary_data[1])
    print("Final synonyms: " + dictionary_data[2])
    print("Final examples: " + dictionary_data[3])
    print("Final etymology: " + dictionary_data[4])
    return dictionary_data

def get_webster_data(word):
    MERRIAM_WEBSTER_DICTIONARY_KEY = os.getenv("MERRIAM_WEBSTER_DICTIONARY_KEY")
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={MERRIAM_WEBSTER_DICTIONARY_KEY}"
    webster_response = requests.get(url)
    webster_response_content_str = webster_response.content.decode()
    webster_top_level_list = json.loads(webster_response_content_str)
    if webster_top_level_list == [] or isinstance(webster_top_level_list[0], str):
        print("Word not found in Webster dictionary")
        return False, False
    else:
        first_entry_id = webster_top_level_list[0]["meta"]["id"].split(":")[0]
        entry_with_same_id_and_with_more_common_spelling_exists = False
        entry_with_same_id_and_without_more_common_spelling_exists = False
        for entry in webster_top_level_list:
            if entry.get("cxs"):# If a "cross reference target" array (more common spelling) exists
                if not entry_with_same_id_and_with_more_common_spelling_exists and entry["meta"]["id"].split(":")[0] == first_entry_id: # if we haven't found one already in another entry
                    more_common_spelling = entry["cxs"][0]["cxtis"][0].get("cxt")# haven't seen example of cxtis array with len > 1, just assume the first one is the one to use
                    entry_with_same_id_and_with_more_common_spelling_exists = True
            else:
                if entry["meta"]["id"].split(":")[0] == first_entry_id:# if it doesn't pass this test, it's just the entry for the more common spelling tacked on, so there isn't actually a unique meaning for the spelling
                    lemma_for_entry_without_more_common_spelling = entry["meta"]["id"].split(":")[0]
                    entry_with_same_id_and_without_more_common_spelling_exists = True
        if entry_with_same_id_and_with_more_common_spelling_exists:
            if not entry_with_same_id_and_without_more_common_spelling_exists:# if all entries point to a more common spelling, with no unique entries for this spelling (e.g. "forbode" would pass this test but "baloney" would not, since it has its own meaning, not just a secondary spelling for "bologna")
                lemma = more_common_spelling
            else: # at least one entry with a more common spelling exist, but there is also a unique entry for this spelling (e.g. "baloney" has its own meaning, not just a secondary spelling for "bologna")
                lemma = lemma_for_entry_without_more_common_spelling
        else:
            lemma = first_entry_id

        print(f"lemma: {lemma}")
        return lemma, webster_top_level_list

def get_wordsapi_data(lemma):
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    wordsapi_url = f"https://wordsapiv1.p.rapidapi.com/words/{lemma}"
    headers = {
        "X-RapidAPI-Key": "70d1a563a7msh45edbe057268788p17ec20jsn49d9b58011e2",
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }
    wordsapi_response = requests.get(wordsapi_url, headers=headers)
    wordsapi_data = json.loads(wordsapi_response.content)
    return wordsapi_data

def extract_wordsapi_data(wordsapi_data, exclude_synonym_result_nums, exclude_example_result_nums):
    definition_str = ""
    synonyms_str = ""
    synonyms_list = []# used to check for duplicates across results
    examples_str = ""
    for count, result in enumerate(wordsapi_data["results"]):
        result_num = count + 1
        if len(wordsapi_data["results"]) > 1:
            result_num_prefix = f"{result_num}. "
        else:
            result_num_prefix = ""

        if result_num != len(wordsapi_data["results"]):
            result_str_suffix = " "
        else:
            result_str_suffix = ""
        
        part_of_speech = result.get("partOfSpeech", "")
        if part_of_speech == "":
            part_of_speech_prefix = ""
        else:
            part_of_speech_prefix = f"({part_of_speech}) "

        definition = result.get("definition", "")
        definition_str += result_num_prefix + part_of_speech_prefix + definition + result_str_suffix
        
        synonyms_list_this_result = result.get("synonyms", [])
        if len(synonyms_list_this_result) > 0 and not exclude_synonym_result_nums:
            synonyms_str += result_num_prefix
        count = 0
        for synonym in synonyms_list_this_result:
            if synonym in synonyms_list:
                continue
            
            if count > 0:
                synonym_prefix = ", "
            else:
                synonym_prefix = ""
            synonyms_str += synonym_prefix + synonym
            synonyms_list.append(synonym)

            count += 1# can't just enumerate since we're skipping some

        if exclude_synonym_result_nums:
            synonym_str_suffix = result_str_suffix.replace(" ", "; ")
        else:
            synonym_str_suffix = result_str_suffix
        if len(synonyms_list_this_result) > 0:
            synonyms_str += synonym_str_suffix

        examples_list = result.get("examples", [])
        if len(examples_list) > 0 and not exclude_example_result_nums:
            examples_str += result_num_prefix
        for count, example in enumerate(examples_list):
            if count > 0:
                example_prefix = "; "
            else:
                example_prefix = ""
            examples_str += example_prefix + example
        if exclude_example_result_nums:
            example_str_suffix = result_str_suffix.replace(" ", "; ")
        else:
            example_str_suffix = result_str_suffix
        if len(examples_list) > 0:
            examples_str += example_str_suffix

    definition_str = misc_helpers.strip_whitespace_and_more(definition_str, non_whitespace_chars_to_strip=",;:-|")
    synonyms_str = misc_helpers.strip_whitespace_and_more(synonyms_str, non_whitespace_chars_to_strip=",;:-|")
    examples_str = misc_helpers.strip_whitespace_and_more(examples_str, non_whitespace_chars_to_strip=",;:-|")

    return definition_str, synonyms_str, examples_str

def extract_webster_data(webster_top_level_list):
    definition_str = ""
    synonyms_str = ""
    examples_str = ""
    etymology = ""
    entry_num = 0

    total_entries = 0
    for entry in webster_top_level_list:
        if entry.get("cxs"): # if "csx" array exists, skip that entry (use the entry with the more common spelling instead -- otherwise there will be duplicate definitions etc)
            pass
        else:
            total_entries += 1

    for entry in webster_top_level_list:
        if entry.get("cxs"): # if "csx" array exists, skip that entry (use the entry with the more common spelling instead -- otherwise there will be duplicate definitions etc)
            continue
        
        # Below, if the "id" for this entry is different than the main "id". e.g. "sow" has an entry with "id" == "self-sow" and "baloney" has an entry with "id" == "bologna". 
        # It's impossible to decide whether to skip or not (would want to skip "self-sow" but not "bologna", e.g.), so just put the different "id" in brackets at the beginning of the definition
        # Other examples include: monitor, feline
        entry_id = entry["meta"]["id"].split(":")[0]
        different_id_from_first_entry_prefix = ""
        if entry_id != webster_top_level_list[0]["meta"]["id"].split(":")[0]:
            different_id_from_first_entry_prefix = f"[{entry_id}] "

        entry_num += 1 # don't just enumerate the for loop since we are skipping some entries above

        part_of_speech = entry.get("fl")
        if not part_of_speech:
            part_of_speech_prefix = ""
        else:
            part_of_speech_prefix = f"({part_of_speech}) "
        
        if total_entries > 1:
            entry_num_prefix = f"{entry_num}. "
        else:
            entry_num_prefix = ""

        try:
            definition_sense_sequence = entry["def"][0]["sseq"]
        except:
            continue
            
        examples_this_entry = []
        definitions_this_entry_str = ""
        synonyms_this_entry_str = ""
        total_senses_in_definition_sense_sequence = 0
        for sense in definition_sense_sequence:
            for sub_sense in sense:
                total_senses_in_definition_sense_sequence += 1
        bs_this_sense = False
        for sense_count, sense in enumerate(definition_sense_sequence):
            sense_num = sense_count + 1
            bs_this_subsense = False
            for sub_sense in sense:
                print(sub_sense)
                if sub_sense[0] == "pseq":# "pseq" includes optional "bs" followed by at least one "sense" for which the value of "sn" (pseq number in parentheses) should be included before the text
                    definitions_this_pseq_str = ""
                    parenthesized_sequence = sub_sense[1]
                    for sub_pseq_count, sub_pseq in enumerate(parenthesized_sequence): 
                        sub_pseq_num = sub_pseq_count + 1
                        if sub_pseq[0] == "bs":# ends in such as, example senses follow. examples include: monitor, 
                            sense_dict = sub_pseq[1]["sense"]
                            sense_definition_text_list = sense_dict["dt"]
                            status_labels_str = get_status_label_string_from_sense_dict(sense_dict)
                            for component in sense_definition_text_list:
                                if component[0] == "text":
                                    definitions_this_pseq_str += status_labels_str + clean_webster_text(component[1])
                                    if sub_pseq_num != len(parenthesized_sequence):
                                        definitions_this_pseq_str += " "
                                if component[0] == "vis":
                                    examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                                    examples_this_entry.extend(examples_to_extend)
                        elif sub_pseq[0] == "sense":# examples following "bs"
                            sense_dict = sub_pseq[1]
                            sense_definition_text_list = sense_dict["dt"]
                            pseq_num_str = sense_dict["sn"]
                            status_labels_str = get_status_label_string_from_sense_dict(sense_dict)
                            for component in sense_definition_text_list:
                                if component[0] == "text":
                                    definitions_this_pseq_str += " " + pseq_num_str + " " + status_labels_str + clean_webster_text(component[1])
                                    definitions_this_pseq_str = definitions_this_pseq_str.replace("  ", " ")
                                    if sub_pseq_num == len(parenthesized_sequence) and sense_num != total_senses_in_definition_sense_sequence:# last in a pseq but not last in definition_sense_sequence
                                        definitions_this_pseq_str += "; "
                                if component[0] == "ca":# haven't found examples of a "ca" within a "sense" within a "pseq" but it should work just like within a "sense" not within a "pseq"
                                    called_also_text_str = get_called_also_text_str_from_ca_dict(component[1])
                                    if definitions_this_pseq_str.endswith("; "):
                                        definitions_this_pseq_str = definitions_this_pseq_str[:-2] + called_also_text_str + "; "
                                    else:
                                        definitions_this_pseq_str = definitions_this_pseq_str + called_also_text_str
                                if component[0] == "uns":# haven't found examples of an "uns" within a "sense" within a "pseq" but it should work just like within a "sense" not within a "pseq"
                                    usage_note = get_usage_note_from_uns_list(component[1])
                                    if definitions_this_pseq_str.endswith("; "):
                                        definitions_this_pseq_str = definitions_this_pseq_str[:-2] + f" ({usage_note}); "
                                    else:
                                        definitions_this_pseq_str = definitions_this_pseq_str + f" ({usage_note})"
                                if component[0] == "vis":
                                    examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                                    examples_this_entry.extend(examples_to_extend)
                        
                        # Regardless of whether the sense is "bs" or "sense", account for adding "sdsense" to the definition text if it's present
                        if sense_dict.get("sdsense"):
                            sense_divider = sense_dict["sdsense"]["sd"]# something like "specifically"
                            for component in sense_dict["sdsense"]["dt"]:
                                if component[0] == "text":
                                    sd_text = clean_webster_text(component[1])
                                    definitions_this_pseq_str += f", {sense_divider} {sd_text}"
                                    if sub_pseq_num != len(parenthesized_sequence):
                                        definitions_this_pseq_str += "; "
                                if component[0] == "vis":
                                    examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                                    examples_this_entry.extend(examples_to_extend)

                    definitions_this_entry_str += f"{definitions_this_pseq_str}"

                # Below: "bs" not within a "pseq" MAY be followed by at least one "sense" for which the value of "sn" (letter not yet in parentheses) should be included before the text; 
                # OR it may just have a "sdsense" within the sense_dict alongside "dt" which should be appended to the "dt" text, just like if it were within a "pseq"
                elif sub_sense[0] == "bs":# examples include: feline, chary
                    bs_this_sense = True
                    bs_this_subsense = True
                    definitions_this_bs_str = ""
                    sense_dict = sub_sense[1]["sense"]
                    sense_definition_text_list = sense_dict["dt"]
                    status_labels_str = get_status_label_string_from_sense_dict(sense_dict)
                    for component in sense_definition_text_list:
                        if component[0] == "text":
                            definitions_this_bs_str += status_labels_str + clean_webster_text(component[1])
                        if component[0] == "vis":
                            examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                            examples_this_entry.extend(examples_to_extend)
                    if sense_dict.get("sdsense"):
                        sense_divider = sense_dict["sdsense"]["sd"]# something like "specifically"
                        for component in sense_dict["sdsense"]["dt"]:
                            if component[0] == "text":
                                sd_text = clean_webster_text(component[1])
                                definitions_this_bs_str += f", {sense_divider} {sd_text}"
                            if component[0] == "vis":
                                examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                                examples_this_entry.extend(examples_to_extend)
                    definitions_this_entry_str += definitions_this_bs_str

                elif sub_sense[0] == "sense":
                    definitions_this_sense_str = ""
                    sense_dict = sub_sense[1]
                    sense_definition_text_list = sense_dict["dt"]
                    status_labels_str = get_status_label_string_from_sense_dict(sense_dict)
                    for component in sense_definition_text_list:
                        if component[0] == "text":
                            if bs_this_sense:# if this subsense follows a "bs" within the same sense. examples include feline, chary. chary has some subsenses that follow a "bs" in the same sense, and also some that follow it in a separate sense)
                                bsseq_num_str = sense_dict.get("sn", "")
                                bsseq_num_str = f" ({bsseq_num_str}) "
                                if not bs_this_subsense:# if a previous subsense followed a "bs", but now this one is not part of the "bs" sequence. examples include: chary
                                    definitions_this_sense_str += "; " + status_labels_str + clean_webster_text(component[1])
                                else:
                                    definitions_this_sense_str += bsseq_num_str + status_labels_str + clean_webster_text(component[1])
                            else:# examples include: monitor
                                definitions_this_sense_str += status_labels_str + clean_webster_text(component[1])
                                if not sense_dict.get("sdsense"):
                                    definitions_this_sense_str += "; "
                        if component[0] == "ca":# examples include: abaca
                            called_also_text_str = get_called_also_text_str_from_ca_dict(component[1])
                            if definitions_this_sense_str.endswith("; "):
                                definitions_this_sense_str = definitions_this_sense_str[:-2] + called_also_text_str + "; "
                            else:
                                definitions_this_sense_str = definitions_this_sense_str + called_also_text_str
                        if component[0] == "uns":# examples include: abeyance
                            usage_note = get_usage_note_from_uns_list(component[1])
                            if definitions_this_sense_str.endswith("; "):
                                definitions_this_sense_str = definitions_this_sense_str[:-2] + f" ({usage_note}); "
                            else:
                                definitions_this_sense_str = definitions_this_sense_str + f" ({usage_note})"
                        if component[0] == "vis":# examples include: monitor
                            examples_to_extend = get_example_str_from_example_dicts_list(component[1])
                            examples_this_entry.extend(examples_to_extend)
                    if sense_dict.get("sdsense"):
                        sense_divider = sense_dict["sdsense"]["sd"]# something like "specifically" or "also"
                        for component in sense_dict["sdsense"]["dt"]:
                            if component[0] == "text":
                                sd_text = clean_webster_text(component[1])
                                definitions_this_sense_str += f", {sense_divider} {sd_text}"
                    definitions_this_entry_str += definitions_this_sense_str

        quotes = entry.get("quotes", [])
        examples_to_extend = get_example_str_from_example_dicts_list(quotes)
        examples_this_entry.extend(examples_to_extend)

        syns = entry.get("syns")
        if syns:
            synonyms_lists = syns[0]["pt"]
            synonyms_text_total_qty = 0
            for synonyms_list in synonyms_lists:
                if synonyms_list[0] == "text":
                    synonyms_text_total_qty += 1

            synonyms_text_count = 0
            for synonyms_list in synonyms_lists:
                if synonyms_list[0] == "text":
                    synonyms_text_count += 1
                    synonyms_this_entry_str += clean_webster_text(synonyms_list[1].replace("{/sc} {sc}", ", ")) + "; "

        if entry_num != total_entries:
            entry_str_suffix = "\n"
        else:
            entry_str_suffix = ""    
        
        definitions_this_entry_str = misc_helpers.strip_whitespace_and_more(definitions_this_entry_str, non_whitespace_chars_to_strip=",;:-|")
        definition_str += entry_num_prefix + part_of_speech_prefix  + different_id_from_first_entry_prefix + definitions_this_entry_str + entry_str_suffix

        if synonyms_this_entry_str != "":
            synonyms_this_entry_str = misc_helpers.strip_whitespace_and_more(synonyms_this_entry_str, non_whitespace_chars_to_strip=",;:-|")
            synonyms_str += entry_num_prefix + different_id_from_first_entry_prefix + synonyms_this_entry_str + entry_str_suffix

        if examples_this_entry != []:
            examples_this_entry_str = "; ".join(examples_this_entry)
            examples_str += entry_num_prefix + different_id_from_first_entry_prefix + examples_this_entry_str + entry_str_suffix

        etymology_list = entry.get("et", [])
        for component in etymology_list:
            if component[0] == "text" and etymology == "" and component[1] != "origin unknown":# only set etymology once (from within the first entry where one is found). etymologies for other entries tend to just refer to the first entry.
                etymology = clean_webster_text(component[1])

    return clean_webster_text(definition_str), clean_webster_text(synonyms_str), clean_webster_text(examples_str), clean_webster_text(etymology)

def get_status_label_string_from_sense_dict(sense_dict):
    status_labels_str = ""
    status_labels_list = sense_dict.get("sls")
    if status_labels_list:
        status_labels_str = ", ".join(status_labels_list)
        status_labels_str = f"[{status_labels_str}] "
    return status_labels_str

def get_example_str_from_example_dicts_list(example_dicts_list):
    examples_to_extend = []
    for example_dict in example_dicts_list:
        author_source_date = ""
        author_dict = example_dict.get("aq")
        if author_dict:
            author = clean_webster_text(author_dict.get("auth"))
            source = clean_webster_text(author_dict.get("source"))
            if author and source:
                author_and_source = f"-{author}, {source}"
            elif author and not source:
                author_and_source = f"-{author}"
            elif source:
                author_and_source = f"-{source}"
            else:
                continue
            date = clean_webster_text(author_dict.get("aqdate"))
            author_source_date = f" {author_and_source}"
            if date:
                author_source_date += f" ({date})"
        example_str = clean_webster_text(example_dict["t"]) + author_source_date
        examples_to_extend.append(example_str)
    
    return examples_to_extend

def get_called_also_text_str_from_ca_dict(ca_dict):
    called_also_text_dicts_list = ca_dict["cats"]
    called_also_text_list = []
    for called_also_text_dict in called_also_text_dicts_list:
        called_also_text_list.append(called_also_text_dict["cat"])
    called_also_text_str = ", ".join(called_also_text_list)
    called_also_text_str = clean_webster_text(called_also_text_str)
    called_also_text_str = ", also called " + called_also_text_str

    return called_also_text_str

def get_usage_note_from_uns_list(uns_list):
    for uns_component in uns_list[0]:
        if uns_component[0] == "text":
            usage_note = clean_webster_text(uns_component[1])
            break
    return usage_note

def clean_webster_text(raw_str):
    if not raw_str:
        return raw_str
    cleaned_str = raw_str
    tokens_to_remove_but_keep_text_between_tokens = ["{b}", "{/b}", "{bc}", "{inf}", "{/inf}", "{it}", "{/it}", "{ldquo}", "{rdquo}", "{sc}", "{/sc}", "{sup}", "{wi}", "{/wi}", "{parahw}", "{/parahw}", "{phrase}", "{/phrase}", "{qword}", "{/qword}", "{mat}"]
    # examples include: absence
    # ^removing {mat} above, which only exists within {ma} tokens. Then remove text within {ma} tokens which would've otherwise included the {mat} tokens
    for token in tokens_to_remove_but_keep_text_between_tokens:
        cleaned_str = cleaned_str.replace(token, "")
        
    tokens_to_replace_with_parentheses = ["{dx}", "{dx_def}", "{dx_ety}"]
    for token_start in tokens_to_replace_with_parentheses:
        token_end = token_start.replace("{", "{/")
        cleaned_str = cleaned_str.replace(token_start, "(")
        cleaned_str = cleaned_str.replace(token_end, ")")
    
    tokens_to_remove_and_remove_text_between_tokens = ["{gloss}", "{ma}"]# examples include: absence
    for token_start in tokens_to_remove_and_remove_text_between_tokens:
        token_end = token_start.replace("{", "{/")
        while token_start in cleaned_str:
            next_token_start_index = cleaned_str.find(token_start)
            next_token_end_index = cleaned_str.find(token_end, next_token_start_index - 1)
            cleaned_str = cleaned_str[:next_token_start_index - 1] + cleaned_str[next_token_end_index + len(token_end):]
                
    tokens_to_strip_and_keep_text_within_same_bracket = ["a_link|", "d_link|", "i_link|", "et_link|", "sx|", "dxt|"]
    for token in tokens_to_strip_and_keep_text_within_same_bracket:
        total_count_this_token_pre_clean = cleaned_str.count(token)
        this_token_found_count = 0
        while token in cleaned_str:
            this_token_found_count += 1
            next_token_index = cleaned_str.find(token)
            next_closing_curly_brace_index = cleaned_str.find("}", next_token_index - 1)
            token_str_to_keep = cleaned_str[next_token_index + len(token):next_closing_curly_brace_index]
            token_str_to_keep = token_str_to_keep.split("|")[0]
            token_str_to_keep = token_str_to_keep.split(":")[0]
            if token == "sx|":# usually meant to be in parentheses, it's a "link" to a synonym. at end of function, will remove parentheses if the whole thing would be in parentheses otherwise
                if total_count_this_token_pre_clean == 1:
                    token_str_to_keep = f"({token_str_to_keep})"# both ()
                else:
                    if this_token_found_count == 1:
                        token_str_to_keep = f"({token_str_to_keep}"# open ( only
                    if this_token_found_count == total_count_this_token_pre_clean:
                        token_str_to_keep = f"{token_str_to_keep})"# closed ) only
            cleaned_str = cleaned_str[:next_token_index - 1] + token_str_to_keep + cleaned_str[next_closing_curly_brace_index + 1:]

    # ignore {ds} token since that's only within "date" (as in date first seen, which isn't used at all)
    cleaned_str = cleaned_str.replace(", ,", ",")
    cleaned_str = cleaned_str.replace("; ;", ";")
    cleaned_str = cleaned_str.replace(" ;", ";")
    cleaned_str = cleaned_str.replace(".;", ";")
    cleaned_str = misc_helpers.strip_whitespace_and_more(cleaned_str, non_whitespace_chars_to_strip=",;:-|")

    #after fully cleaning, check if it starts and ends with parentheses (and only has one set), and remove them if so. this is mostly for definitions that are just "sx|"" tokens:
    if cleaned_str.count("(") == 1 and cleaned_str.count(")") == 1 and cleaned_str[0] == "(" and cleaned_str[-1] == ")":
        cleaned_str = cleaned_str[1:-1]

    return cleaned_str

# Oxford English Dictionary (no longer available free):
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

# def get_oed_dictionary_data(word):
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