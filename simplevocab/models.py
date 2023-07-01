from django.db import models
from django.core.validators import MinLengthValidator
from django.conf import settings

class Word(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    word = models.CharField(
        max_length=50,
        null=False
    )
    definition = models.CharField(max_length=255)
    synonyms = models.CharField(max_length=255)
    examples = models.CharField(max_length=255)
    etymology = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)#should maybe remove null=True eventually

    # Shows up in the admin list
    def __str__(self):
        return self.word
    
class VocabEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)#should maybe remove null=True eventually
    word = models.ForeignKey('Word', on_delete=models.CASCADE, null=False)
    discovery_source = models.CharField("Discovery Source", max_length=255)
    last_quiz = models.BooleanField(default=False)
    definition_override = models.CharField("Your Definition", max_length=255, default="", null=True, blank=True)
    synonyms_override = models.CharField("Your Synonyms", max_length=255, default="", null=True, blank=True)
    examples_override = models.CharField("Your Examples", max_length=255, default="", null=True, blank=True)
    etymology_override = models.CharField("Your Etymology", max_length=255, default="", null=True, blank=True)
    discovery_context = models.CharField("Discovery Context", max_length=255, default="", null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.word, self.user)
    
class QuizResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vocab_entry = models.ForeignKey('VocabEntry', on_delete=models.CASCADE, null=True)
    correct_answer = models.BooleanField(default=False)

    def __str__(self):
        if self.correct_answer == True:
            self.correct_answer_str = "Correct"
        else:
            self.correct_answer_str = "Incorrect"
        return "Response for the word '{}' at {}: {}".format(self.vocab_entry, self.created_at, self.correct_answer_str)
