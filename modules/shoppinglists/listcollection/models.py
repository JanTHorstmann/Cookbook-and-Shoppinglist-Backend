from django.db import models
from modules.custom_user.models import CustomUser
from django.contrib.auth import get_user_model

class ListCollection(models.Model):
    name = models.CharField(max_length=50, blank=False)
    participants = models.ManyToManyField(CustomUser, related_name="shared_collections")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="owned_lists")

    def __str__(self):
        return f"{self.name} Author:{self.author} {self.author.id}"