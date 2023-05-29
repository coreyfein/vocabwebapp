from simplevocab.models import Word, VocabEntry, QuizResponse
import pprint

def run(user, words_per_quiz):
    unquizzed_vocabentry_objects = []
    quizzed_vocabentry_objects = []
    user_responses = QuizResponse.objects.filter(user=user).order_by("-created_at")
    vocab_entry_streaks = {}
    for user_response in user_responses:
        if user_response.vocab_entry not in quizzed_vocabentry_objects:# only most recent response caught here
            quizzed_vocabentry_objects.append(user_response.vocab_entry)
            if user_response.correct_answer == False:# most recent response was incorrect
                vocab_entry_streaks[user_response.vocab_entry] = {
                    "streak_status": "ongoing",
                    "streak": -1,
                    "most_recent_quiz_date": user_response.created_at
                }
            else:# most recent response was correct
                vocab_entry_streaks[user_response.vocab_entry] = {
                    "streak_status": "ongoing",
                    "streak": 1,
                    "most_recent_quiz_date": user_response.created_at
                }
                
        else:# this is at least the second most recent response
            if user_response.correct_answer == False:
                if vocab_entry_streaks[user_response.vocab_entry]["streak"] < 0 and vocab_entry_streaks[user_response.vocab_entry]["streak_status"] == "ongoing":
                    vocab_entry_streaks[user_response.vocab_entry]["streak"] -= 1
                else:
                    vocab_entry_streaks[user_response.vocab_entry]["streak_status"] = "ended"
            if user_response.correct_answer == True:    
                if vocab_entry_streaks[user_response.vocab_entry]["streak"] > 0 and vocab_entry_streaks[user_response.vocab_entry]["streak_status"] == "ongoing":
                    vocab_entry_streaks[user_response.vocab_entry]["streak"] += 1
                else:
                    vocab_entry_streaks[user_response.vocab_entry]["streak_status"] = "ended"
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(vocab_entry_streaks)
    quizzed_queue_no_cap = sorted(vocab_entry_streaks, key=lambda x: (-vocab_entry_streaks[x]["streak"], vocab_entry_streaks[x]["most_recent_quiz_date"]), reverse=True)
    # above sorts by -streak first, then most recent quiz date. that would make higher streaks first, then oldest most_recent_quiz_date. both are then reversed, making it sorted by lowest streak, then newest most_recent_quiz_date
    if len(quizzed_queue_no_cap) >= words_per_quiz:
        quizzed_queue = quizzed_queue_no_cap[:words_per_quiz]# caps quizzed_queue at words_per_quiz if necessary
    else:
        quizzed_queue = quizzed_queue_no_cap
            
    # Set qty of unquizzed words to enter queue, build unquizzed_queue
    user_vocabentries = VocabEntry.objects.filter(user=user).order_by("created_at")
    for vocab_entry in user_vocabentries:
        if vocab_entry not in quizzed_queue_no_cap:
            unquizzed_vocabentry_objects.append(vocab_entry)
    unquizzed_queue = []
    quizzed_queue_qty = len(quizzed_queue)
    if words_per_quiz - quizzed_queue_qty > 5:
        max_unquizzed_words = words_per_quiz - quizzed_queue_qty
    else:
        max_unquizzed_words = 5
    for count, unquizzed_vocabentry_object in enumerate(unquizzed_vocabentry_objects):
        if count < max_unquizzed_words:
            unquizzed_queue.append(unquizzed_vocabentry_object)
        else:
            break
    full_queue = unquizzed_queue + quizzed_queue
    print(unquizzed_queue)
    print(quizzed_queue)
    print(full_queue)
    print(len(full_queue))
    return(full_queue)

if __name__ == "__main__":
    run()