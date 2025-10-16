from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from modules.cookbook.ingredients.models import Ingredient
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()
class IngredientTestCase(TestCase):
    def setUp(self):
        """
        Set up two initial ingredients for testing.
        """    
        Ingredient.objects.create(name="Mehl")
        Ingredient.objects.create(name="brot")

    def test_ingredients_save_in_lowercase(self):
        """
        Ensure that ingredients are saved in lowercase in the database.
        """
        ingredient = Ingredient.objects.create(name="Zucker")
        self.assertEqual(ingredient.name, "zucker")

    def test_ingredient_str_representation(self):
        """
        Verify that the string representation of an ingredient capitalizes the first letter.
        """
        ingredient = Ingredient.objects.create(name="zucker")
        self.assertEqual(str(ingredient), "Zucker")

    def test_ingredient_unique_constraint(self):
        """
        Ensure that duplicate ingredients (case-insensitive) cannot be created.
        """
        Ingredient.objects.create(name="zucker")
        with self.assertRaises(Exception):  # Sollte einen Fehler werfen
            Ingredient.objects.create(name="ZUCKER") 

    def test_ingredient_empty_name(self):
        """
        Ensure that creating an ingredient with an empty name raises a ValueError.
        """
        with self.assertRaises(ValueError):  # Erwarte jetzt explizit ValueError
            Ingredient.objects.create(name=" ")

    def test_case_insensitive_ingredient(self):
        """
        Test that ingredients are case-insensitively unique.
        """
        Ingredient.objects.create(name="Salz")
        with self.assertRaises(Exception):
            Ingredient.objects.create(name="SALZ")  

class IngredientAPITestCase(APITestCase):
    def setUp(self):
        """        
        Set up two ingredients and prepare the API URL for list endpoints.
        """
        self.user1 = User.objects.create_user(email="user1@example.com", password="testpassword123")
        self.client.force_authenticate(user=self.user1)
        
        self.ingredient1 = Ingredient.objects.create(name="mehl")
        self.ingredient2 = Ingredient.objects.create(name="brot")
        self.url = reverse("ingredients-list")

    def test_get_ingredients(self):
        """
        Test retrieving the list of ingredients via the API.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Erwartet 2 Zutaten
        self.assertEqual(response.data[0]["name"], "Mehl")  # Großbuchstabe!
        self.assertEqual(response.data[1]["name"], "Brot")

    def test_create_ingredient_success(self):
        """
        Test successfully creating a new ingredient via the API.
        """
        data = {"name": "Käse"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(name="käse").exists())

    def test_create_duplicate_ingredient(self):
        """
        Ensure that creating a duplicate ingredient (case-insensitive) returns a 400 error.
        """
        data = {"name": "Mehl"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "This ingredient already exists!")

    def test_create_empty_ingredient(self):
        """
        Ensure that creating an ingredient with an empty name returns a 400 error.
        """
        data = {"name": ""}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_ingredient_detail(self):
        """
        Test retrieving a single ingredient by its ID.
        """
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Mehl")

    def test_update_ingredient(self):
        """
        Test updating an existing ingredient via the API.
        """
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        data = {"name": "Weizenmehl"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Weizenmehl".capitalize())

    def test_delete_ingredient(self):
        """
        Test deleting an ingredient via the API.
        """
        url = reverse("ingredients-detail", kwargs={"pk": self.ingredient1.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient1.id).exists())