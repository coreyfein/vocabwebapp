from simplevocab.models import QuizResponse, VocabEntry

def run(cleaned_data, user):   
    quiz_responses_added = [] 
    for vocab_entry in cleaned_data:
        vocab_entry_id = int(vocab_entry.replace("vocab_entry_", ""))
        v = VocabEntry.objects.get(id=vocab_entry_id)
        correct_answer = cleaned_data[vocab_entry]
        q = QuizResponse.objects.create(user=user, vocab_entry=v, correct_answer=correct_answer)
        q.save()
        quiz_responses_added.append(q)
    return quiz_responses_added
    

if __name__ == "__main__":
    run()