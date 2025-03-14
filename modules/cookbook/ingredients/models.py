from django.db import models

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False, null=False)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower()
        if not self.name:
            raise ValueError("Ingredient name cannot be empty")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.capitalize()
