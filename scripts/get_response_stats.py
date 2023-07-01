from simplevocab.models import Word, VocabEntry, QuizResponse

def run(user):
    response_stats = {}
    user_responses = QuizResponse.objects.filter(user=user).order_by("-created_at")
    vocab_entries = VocabEntry.objects.filter(user=user).order_by("-created_at")
    for vocab_entry in vocab_entries:
        # if not vocab_entry.definition_override or vocab_entry.definition_override == "":
        #     definition = vocab_entry.word.definition
        # if not vocab_entry.synonyms_override or vocab_entry.synonyms_override == "":
        #     synonyms = vocab_entry.word.synonyms
        # dictionary_data_str = """Definition: {}
        # Synonyms: {}
        # """.format(definition, synonyms)
        # print("dictionary_data_str")
        # print(dictionary_data_str)
        response_stats[vocab_entry.word.word] = {
            "all_time":{
                "correct": 0, 
                "total":0,
                "percent_correct": 0.0,
                },
            "last_ten":{
                "correct": 0,
                "total": 0,
                "percent_correct": 0.0
                },
            "streak": "Not yet quizzed",
            "streak_status": "ongoing",
            "discovery_source": vocab_entry.discovery_source,
            "discovery_context": vocab_entry.discovery_context,
            # "dictionary_data_str": dictionary_data_str
        }
    for user_response in user_responses:
        word = str(user_response.vocab_entry.word)
        response_stats[word]["all_time"]["total"] += 1

        if user_response.correct_answer:
            response_stats[word]["all_time"]["correct"] += 1
            if response_stats[word]["streak"] == "Not yet quizzed":
                response_stats[word]["streak"] = 1
            elif response_stats[word]["streak"] > 0 and response_stats[word]["streak_status"] == "ongoing":
                response_stats[word]["streak"] += 1
            else:
                response_stats[word]["streak_status"] = "ended"
        else:
            if response_stats[word]["streak"] == "Not yet quizzed":
                response_stats[word]["streak"] = -1
            elif response_stats[word]["streak"] < 0 and response_stats[word]["streak_status"] == "ongoing":
                response_stats[word]["streak"] -= 1
            else:
                response_stats[word]["streak_status"] = "ended"
            

        if response_stats[word]["all_time"]["correct"] > 0:
            response_stats[word]["all_time"]["percent_correct"] = round(response_stats[word]["all_time"]["correct"] / response_stats[word]["all_time"]["total"] * 100)
        else:
            response_stats[word]["all_time"]["percent_correct"] = 0
        
        if response_stats[word]["all_time"]["total"] <= 10:
            response_stats[word]["last_ten"]["total"] += 1
            if user_response.correct_answer:
                response_stats[word]["last_ten"]["correct"] += 1
            if response_stats[word]["last_ten"]["correct"] > 0:
                response_stats[word]["last_ten"]["percent_correct"] = round(response_stats[word]["last_ten"]["correct"] / response_stats[word]["last_ten"]["total"] * 100)
            else:
                response_stats[word]["last_ten"]["percent_correct"] = 0
            
    return response_stats

if __name__ == "__main__":
    run()