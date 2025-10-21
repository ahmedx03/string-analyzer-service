from django.db import models
import hashlib

class StringAnalysis(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def to_response_dict(self):
        return {
            "id": self.id,
            "value": self.value,
            "properties": {
                "length": self.length,
                "is_palindrome": self.is_palindrome,
                "unique_characters": self.unique_characters,
                "word_count": self.word_count,
                "sha256_hash": self.id,
                "character_frequency_map": self.character_frequency
            },
            "created_at": self.created_at.isoformat()
        }