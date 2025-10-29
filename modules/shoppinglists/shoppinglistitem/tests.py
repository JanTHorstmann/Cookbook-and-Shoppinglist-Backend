from rest_framework.test import APITestCase
from modules.shoppinglists.shoppinglistitem.models import ShoppingListItem
from modules.shoppinglists.listcollection.models import ListCollection
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from modules.cookbook.ingredients.models import Ingredient
from modules.shoppinglists.shoppinglistitem.serializers import ShoppingListItemSerializer

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
        cls.shopping_list_user1_detail_url = reverse("shoppinglistitem-detail", kwargs={"pk": cls.shopping_list_list_user1.id})

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

class ShoppingListPostTests(BaseShoppingListSetup):
    """
    Tests for creating and validating shopping list items
    in the Cookbook & ShoppingList application.

    These tests cover:
    - Successful creation of new items
    - Increasing quantity for existing ingredients
    - Permission restrictions for foreign lists
    - Validation errors for invalid input data
    """

    def test_an_item_can_be_successfully_created_in_a_separate_list(self):
        """
        A new shopping list item can be successfully created
        when the ingredient does not already exist in the list.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ingredient"], "Nudeln")
        self.assertEqual(response.data["unit"], "Gramm")


    def test_existing_item_increases_quantity(self):
        """
        If an ingredient already exists in the same shopping list,
        its amount is increased instead of creating a duplicate item.
        """
        self.client.force_authenticate(user=self.user1)

        existing_item = self.shopping_list_list_user1
        previous_amount = existing_item.amount

        data = {
        "ingredient": "tomaten",
        "amount": 6,
        "unit": "Stück",
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")
        expected_amount = previous_amount + data["amount"]

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["ingredient"], "Tomaten")
        self.assertEqual(float(response.data["amount"]), float(expected_amount))
        self.assertEqual(ShoppingListItem.objects.count(), 1)


    def test_user_cannot_add_items_to_foreign_lists(self):
        """
        A user cannot add items to a shopping list
        where they are neither the author nor a participant.
        """
        self.client.force_authenticate(user=self.user3)
        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to add items to this shopping list.")


    def test_invalid_data_name(self):
        """
        An empty ingredient name should return a 400 Bad Request.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
        "ingredient": "",
        "amount": 500,
        "unit": 'Gramm',
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_data_amount(self):
        """
        A missing or invalid amount should return a 400 Bad Request.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
        "ingredient": "Nudeln",
        "amount": '',
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_data_unit(self):
        """
        An empty unit should return a 400 Bad Request.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "",
        "shopping_list": self.list_user1.id
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_invalid_data_shopping_list_id(self):
        """
        A missing or invalid shopping list ID should return a 400 Bad Request.
        """
        self.client.force_authenticate(user=self.user1)
        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "Gramm",
        "shopping_list": ''
        }
        response = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ShoppingListEditTests(BaseShoppingListSetup):

    def test_author_can_edit_items(self):
        self.client.force_authenticate(user=self.user1)

        data = {
        "ingredient": "tomaten",
        "amount": 6,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response = self.client.patch(self.shopping_list_user1_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_participant_can_edit_items(self):
        self.client.force_authenticate(user=self.user2)

        data = {
        "ingredient": "tomaten",
        "amount": 6,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response = self.client.patch(self.shopping_list_user1_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_non_participant_and_non_author_can_not_edit_items(self):
        self.client.force_authenticate(user=self.user3)

        data = {
        "ingredient": "tomaten",
        "amount": 6,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }

        response = self.client.patch(self.shopping_list_user1_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to edit this item.")

class ShoppingListDeleteTests(BaseShoppingListSetup):

    def test_author_can_delete_item(self):
        self.client.force_authenticate(user=self.user1)

        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response_post = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        delete_id = response_post.data["id"]

        url = f"/api/shoppinglistitem/{delete_id}/"
        response_delete = self.client.delete(url)

        self.assertEqual(response_delete.status_code, 204)
        self.assertFalse(ShoppingListItem.objects.filter(id=delete_id).exists())


    def test_participant_can_delete_item(self):
        self.client.force_authenticate(user=self.user2)

        data = {
        "ingredient": "Nudeln",
        "amount": 500,
        "unit": "Gramm",
        "shopping_list": self.list_user1.id
        }
        response_post = self.client.post(self.shopping_list_url, data, format="json")

        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        delete_id = response_post.data["id"]

        url = f"/api/shoppinglistitem/{delete_id}/"
        response_delete = self.client.delete(url)

        self.assertEqual(response_delete.status_code, 204)
        self.assertFalse(ShoppingListItem.objects.filter(id=delete_id).exists())

class ShoppingListItemSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="123456")
        self.list = ListCollection.objects.create(name="Testlist", author=self.user)
        self.ingredient = Ingredient.objects.create(name="apfel")

    def test_serializer_returns_instance(self):
        data = {
            "ingredient": self.ingredient.name,
            "amount": 2,
            "unit": "kg",
            "shopping_list": self.list.id
        }
        serializer = ShoppingListItemSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        item = serializer.save()
        self.assertIsInstance(item, ShoppingListItem)


    def test_serializer_does_not_create_duplicate(self):
        data1 = {
            "ingredient": self.ingredient.name,
            "amount": 2,
            "unit": "kg",
            "shopping_list": self.list.id
        }
        serializer1 = ShoppingListItemSerializer(data=data1)
        self.assertTrue(serializer1.is_valid(), serializer1.errors)
        item1 = serializer1.save()

        data2 = {
            "ingredient": self.ingredient.name,
            "amount": 3,
            "unit": "kg",
            "shopping_list": self.list.id
        }
        serializer2 = ShoppingListItemSerializer(data=data2)
        self.assertTrue(serializer2.is_valid(), serializer2.errors)
        item2 = serializer2.save()

        self.assertEqual(item1.id, item2.id)
        self.assertEqual(item2.amount, 5)