from django.db import models
from modules.cookbook.ingredients.models import Ingredient 

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="ingredient_recipes")
    amount = models.CharField(max_length=50)

    class Meta:
        unique_together = ("ingredient", "amount")

    def __str__(self):
        return f"{self.amount} {self.ingredient.name}"