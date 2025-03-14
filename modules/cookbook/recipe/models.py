from django.db import models
from django.contrib.auth import get_user_model
from modules.cookbook.ingredients.models import Ingredient 
class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", "Einfach"),
        ("medium", "Mittel"),
        ("hard", "Schwierig"),
    ]

    name = models.CharField(max_length=255)
    instructions = models.TextField()  # Zubereitung
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # User-Verknüpfung
    ingredients = models.ManyToManyField(Ingredient, through="RecipeIngredient")  # Many-to-Many mit Zwischentabelle

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField(max_length=50)

    class Meta:
        unique_together = ("recipe", "ingredient")

    def __str__(self):
        return f"{self.amount} {self.ingredient.name} für {self.recipe.name}"   
