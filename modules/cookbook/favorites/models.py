from django.db import models
from django.contrib.auth import get_user_model
from modules.cookbook.recipe.models import Recipe

class Favorite(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_recipe_favorite"
            )
        ]

        indexes = [
            models.Index(fields=["user", "recipe"]),
        ]

    def __str__(self):
        return f"{self.user} ♥ {self.recipe}"

