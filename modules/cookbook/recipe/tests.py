from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Recipe
from modules.cookbook.recipe_ingredients.models import RecipeIngredient
from modules.cookbook.ingredients.models import Ingredient
from django.db.utils import IntegrityError

class RecipeTestCase(TestCase):
    def setUp(self):
        """
        Set up a user, an ingredient, a recipe ingredient, and a recipe for testing.
        """
        user = get_user_model().objects.create_user(
            email="testuser@example.com",
            username="testuser",
            password="password"
        )
        
        self.ingredient = Ingredient.objects.create(name="Ei")
        self.recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=self.ingredient, 
            amount="1 Stück"
        )

        recipe = Recipe.objects.create(
            name="Spiegelei",
            instructions="Ei in die Pfanne geben und solange an braten bis das Eiweiß geronnen ist",
            preparation_time=10,
            difficulty="easy",
            author=user
        )
        recipe.ingredients.add(self.recipe_ingredient)

    def test_recipe_creation(self):
        """
        Test that a recipe is correctly created with the expected attributes.
        """
        recipe = Recipe.objects.get(name="spiegelei")
        self.assertEqual(recipe.name, "spiegelei")
        self.assertEqual(recipe.instructions, "Ei in die Pfanne geben und solange an braten bis das Eiweiß geronnen ist")
        self.assertEqual(recipe.preparation_time, 10)
        self.assertEqual(recipe.difficulty, "easy")
        self.assertTrue(recipe.ingredients.count(), 1)

    def test_recipe_str_method(self):
        """
        Verify that the string representation of a recipe capitalizes the first letter.
        """
        recipe = Recipe.objects.get(name="spiegelei")
        self.assertEqual(str(recipe), "Spiegelei")

    def test_recipe_creation_without_required_fields(self):
        """
        Ensure that creating a recipe without required fields raises an IntegrityError.
        """
        with self.assertRaises(IntegrityError):
            Recipe.objects.create(
                name="",
                instructions="",
                preparation_time=None,
                difficulty="",
                author=None
            )

    def test_recipe_has_correct_ingredient(self):
        """
        Verify that the created recipe includes the correct recipe ingredient.
        """
        recipe = Recipe.objects.get(name="spiegelei")
        self.assertIn(self.recipe_ingredient, recipe.ingredients.all())

    def test_recipe_deletion(self):
        """
        Test that deleting a recipe removes it from the database.
        """
        recipe = Recipe.objects.get(name="spiegelei")
        recipe.delete()
        self.assertFalse(Recipe.objects.filter(name="spiegelei").exists())