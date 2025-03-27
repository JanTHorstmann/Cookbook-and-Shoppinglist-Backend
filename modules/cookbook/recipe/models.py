from django.db import models
from django.contrib.auth import get_user_model
from modules.cookbook.recipe_ingredients.models import RecipeIngredient
class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Einfach"),
        ("medium", "Mittel"),
        ("hard", "Schwierig"),
    ]

    name = models.CharField(max_length=255)
    instructions = models.TextField()
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(RecipeIngredient)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.capitalize()