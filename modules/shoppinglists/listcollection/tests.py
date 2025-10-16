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
        self.user3 = User.objects.create_user(
            email="user3@example.com", password="testpassword123"
        )
        self.user4 = User.objects.create_user(
            email="user4@example.com", password="testpassword123"
        )

        self.list_user1 = ListCollection.objects.create(
            name="User1 Liste", author=self.user1
        )
        self.list_user2 = ListCollection.objects.create(
            name="User2 Liste", author=self.user2
        )        
        self.list_user1.participants.add(self.user2)
        self.list_user1.participants.add(self.user4)

        self.list_collections_url = reverse("listcollection-list")
        self.leave_url_list_user1 = reverse("listcollection-leave-list", args=[self.list_user1.id])
        self.add_url_list_user1 = reverse("listcollection-add-participant", args=[self.list_user1.id])
        self.remove_url_list_user1 = reverse("listcollection-remove-participant", args=[self.list_user1.id])


class ListCollectionCommonTests(BaseListCollectionSetup):

    def test_authenticated_user_can_retrieve_own_lists(self):
        """Ein authentifizierter User soll nur seine eigenen Listen sehen."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.list_user1.name)
        self.assertEqual(response.data[0]["author"], self.user1.id)


    def test_create_without_name(self):
        self.client.force_authenticate(user=self.user1)    
        response = self.client.post(self.list_collections_url, {"name": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Name cannot be empty or whitespace.", response.data["name"])

    def test_create_whitespace_name(self):
        self.client.force_authenticate(user=self.user1)    
        response = self.client.post(self.list_collections_url, {"name": "   "})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Name cannot be empty or whitespace.", response.data["name"])


    def test_authenticated_user_can_see_lists_where_they_are_participant(self):
        """Ein eingeloggter User soll Listen sehen, bei denen er als Teilnehmer eingetragen ist."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_collections_url)

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
        response = self.client.get(self.list_collections_url)
        list_user1_data = next(
            (l for l in response.data if l["id"] == self.list_user1.id), None
        )
        participants_field = list_user1_data["participants"]

        self.assertIsInstance(participants_field, list)
        self.assertTrue(all(isinstance(p, int) for p in participants_field))


    def test_unauthenticated_users_get_401_unauthorized(self):
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_creating_a_list_automatically_sets_the_logged_in_user_as_the_author(self):
        self.client.force_authenticate(user=self.user1)
        create_response = self.client.post(self.list_collections_url, {"name": "Testliste"})
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(self.list_collections_url)
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


class ListCollectionParticipantsLeaveTests(BaseListCollectionSetup):

    def test_participants_can_successfully_leave_the_list(self):        
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.leave_url_list_user1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "You have left the list.")


    def test_author_cannot_leave_the_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.leave_url_list_user1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You are not a participant of this list.")


class ListCollectionAuthorAddParticipantsTests(BaseListCollectionSetup):

    def test_author_can_add_participants(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Participant added successfully.")


    def test_participant_already_added(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is already a participant.")


    def test_adding_a_non_existent_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 5})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "User does not exist.")


    def test_only_author_can_add_participants(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can add participants.")


    def test_author_cannot_added_to_participants(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 1})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Author is already the owner of this list.")

class ListCollectionAuthorRemoveParticipantsTests(BaseListCollectionSetup):

    def test_only_author_can_remove_participants(self):
        self.client.force_authenticate(user=self.user4)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can remove participants.")


    def test_remove_a_non_existent_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 5})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "User does not exist.")


    def test_remove_a_non_participant_user(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is not a participant.")


    def test_author_can_remove_participants(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Participant removed successfully.")

    def test_created_at_and_updated_at_are_set_automatically(self):
        pass