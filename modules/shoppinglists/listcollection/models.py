from django.db import models
from modules.custom_user.models import CustomUser
from django.contrib.auth import get_user_model

class ListCollection(models.Model):
    name = models.CharField(max_length=50, blank=True)
    participants = models.ManyToManyField(CustomUser, related_name="shared_collections", blank=True)
    author = models.ForeignKey(get_user_model(),blank=False, on_delete=models.CASCADE, related_name="owned_lists")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Author: {self.author.email})"

    def can_delete(self, user):
        """Nur der Autor darf löschen."""
        return self.author == user

    def can_leave(self, user):
        """Teilnehmer dürfen sich selbst entfernen."""
        return user in self.participants.all()