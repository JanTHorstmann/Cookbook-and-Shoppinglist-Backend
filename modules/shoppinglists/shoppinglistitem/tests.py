from rest_framework.test import APITestCase
from modules.shoppinglists.shoppinglistitem.models import ShoppingListItem
from modules.shoppinglists.listcollection.models import ListCollection
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from modules.cookbook.ingredients.models import Ingredient

User = get_user_model()


class BaseShoppingListSetup(APITestCase):
    """
    Base setup class for all shopping list tests.
    Creates test users, list collections, and sample shopping list items.
    """
    @classmethod
    def setUpTestData(cls):
        # --- Create Users ---
        cls.user1 = User.objects.create_user(
            email="user1@example.com", password="testpassword123"
        )
        cls.user2 = User.objects.create_user(
            email="user2@example.com", password="testpassword123"
        )
        cls.user3 = User.objects.create_user(
            email="user3@example.com", password="testpassword123"
        )
        cls.user4 = User.objects.create_user(
            email="user4@example.com", password="testpassword123"
        )

        # --- Create List Collections ---
        cls.list_user1 = ListCollection.objects.create(
            name="User1 Liste", author=cls.user1
        )
        cls.list_user2 = ListCollection.objects.create(
            name="User2 Liste", author=cls.user2
        )

        # --- Create Ingredient ---
        cls.ingredient_tomato = Ingredient.objects.create(name="tomaten")

        # --- Create Shopping List Item for user1 ---
        cls.shopping_list_list_user1 = ShoppingListItem.objects.create(
            ingredient= cls.ingredient_tomato, 
            amount= 4, 
            unit= "Stück", 
            shopping_list= cls.list_user1
        )        

        # --- Add participants to list_user1 ---
        cls.list_user1.participants.add(cls.user2)
        cls.list_user1.participants.add(cls.user4)

        # --- API Endpoints ---
        cls.list_collections_url = reverse("listcollection-list")
        cls.shopping_list_url = reverse("shoppinglistitem-list")

class ShoppingListAuthTests(BaseShoppingListSetup):
    """
    Tests authentication and access control for shopping list endpoints.
    """
    def test_unauthenticated_users_get_401_unauthorized(self):
        """
        Unauthenticated users cannot access any list collections (401 Unauthorized).
        """
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_authenticated_user_can_retrieve_own_lists(self):
        """
        Authenticated users can only see their own list collections.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.list_user1.name)
        self.assertEqual(response.data[0]["author"], self.user1.id)


class ShoppingListGetTests(BaseShoppingListSetup):
    """
    Tests for retrieving shopping list items depending on user access rights.
    """
    def test_user_sees_items_in_his_own_list(self):
        """
        The author of a list can see all their own shopping list items.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.shopping_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["ingredient"], self.shopping_list_list_user1.ingredient.name.capitalize())
        self.assertEqual(response.data[0]["amount"], f"{self.shopping_list_list_user1.amount:.2f}")
        self.assertEqual(response.data[0]["unit"], self.shopping_list_list_user1.unit)
        self.assertEqual(response.data[0]["shopping_list"], self.shopping_list_list_user1.shopping_list.id)


    def test_user_sees_items_from_lists_in_which_he_is_a_participant(self):
        """
        A participant can see shopping list items from lists they were added to.
        """
        self.client.force_authenticate(user=self.user4)
        response = self.client.get(self.shopping_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
        response.data[0]["shopping_list"], self.list_user1.id
    )


    def test_user_cannot_see_items_from_foreign_lists(self):
        """
        A user cannot see shopping list items from lists
        where they are neither the author nor a participant.
        """
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.shopping_list_url)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)