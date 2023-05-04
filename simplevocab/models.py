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
    definition = models.CharField(max_length=255, null=False)
    synonyms = models.CharField(max_length=255)
    examples = models.CharField(max_length=255)
    etymology = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Shows up in the admin list
    def __str__(self):
        return self.word
    
class VocabEntry(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.CASCADE, null=False)
    discovery_source = models.CharField(max_length=50)
    last_quiz = models.BooleanField(default=False)

    def __str__(self):
        return "{} ({})".format(self.word, self.user)
    
class QuizResponse(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.ForeignKey('Word', on_delete=models.CASCADE, null=False)
    correct_answer = models.BooleanField(default=False)

    def __str__(self):
        return "Response for the word '{}' at {}: {}".format(self.word, self.created_at, self.correct_answer)
