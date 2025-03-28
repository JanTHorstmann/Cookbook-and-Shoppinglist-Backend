from django.db import models
from modules.cookbook.ingredients.models import Ingredient 
from django.core.exceptions import ValidationError

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="ingredient_recipes")
    amount = models.CharField(max_length=50, blank=False)

    class Meta:
        unique_together = ("ingredient", "amount")

    def save(self, *args, **kwargs):
        if not self.amount.strip():
            raise ValidationError("Amount cannot be empty")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amount} {self.ingredient.name.capitalize()}"