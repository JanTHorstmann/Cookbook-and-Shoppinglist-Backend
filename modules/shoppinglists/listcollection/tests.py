from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from modules.shoppinglists.listcollection.models import ListCollection
User = get_user_model()


class BaseListCollectionSetup(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="testpassword123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="testpassword123"
        )

        self.list_user1 = ListCollection.objects.create(
            name="User1 Liste", author=self.user1
        )
        self.list_user2 = ListCollection.objects.create(
            name="User2 Liste", author=self.user2
        )        
        self.list_user1.participants.add(self.user2)

        self.url = reverse("listcollection-list")

class ListCollectionCommonTests(BaseListCollectionSetup):

    def test_authenticated_user_can_retrieve_own_lists(self):
        """Ein authentifizierter User soll nur seine eigenen Listen sehen."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.list_user1.name)
        self.assertEqual(response.data[0]["author"], self.user1.id)


    def test_authenticated_user_can_see_lists_where_they_are_participant(self):
        """Ein eingeloggter User soll Listen sehen, bei denen er als Teilnehmer eingetragen ist."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        list_names = [l["name"] for l in response.data]

        self.assertIn(self.list_user1.name, list_names)
        self.assertIn(self.list_user2.name, list_names)

        list_user1_data = next(
            (l for l in response.data if l["id"] == self.list_user1.id), None
        )

        self.assertIsNotNone(list_user1_data)
        self.assertIn(self.user2.id, list_user1_data["participants"])


    def test_participants_field_is_the_correct_type(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        list_user1_data = next(
            (l for l in response.data if l["id"] == self.list_user1.id), None
        )
        participants_field = list_user1_data["participants"]

        self.assertIsInstance(participants_field, list)
        self.assertTrue(all(isinstance(p, int) for p in participants_field))


    def test_unauthenticated_users_get_401_unauthorized(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_creating_a_list_automatically_sets_the_logged_in_user_as_the_author(self):
        self.client.force_authenticate(user=self.user1)
        create_response = self.client.post(self.url, {"name": "Testliste"})
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        list_user1_data = next(
            (l for l in response.data if l["name"] == "Testliste"), None
        )
        self.assertIsNotNone(list_user1_data)
        self.assertEqual(list_user1_data["author"], self.user1.id)


    def test_author_can_delete_own_list(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("listcollection-detail", args=[self.list_user1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ListCollection.objects.filter(id=self.list_user1.id).exists())


    def test_non_author_cannot_delete_list(self):
        """Ein anderer User darf die Liste nicht löschen."""
        self.client.force_authenticate(user=self.user2)
        url = reverse("listcollection-detail", args=[self.list_user1.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can delete this list.")
        self.assertTrue(ListCollection.objects.filter(id=self.list_user1.id).exists())

