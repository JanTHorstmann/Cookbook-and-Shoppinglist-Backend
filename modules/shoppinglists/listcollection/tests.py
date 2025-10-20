from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from modules.shoppinglists.listcollection.models import ListCollection
from django.utils import timezone
import time

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
        """
        Ensures that an authenticated user can only retrieve their own list collections.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.list_user1.name)
        self.assertEqual(response.data[0]["author"], self.user1.id)


    def test_create_without_name(self):
        """
        Ensures that creating a list without a name returns a validation error.
        """
        self.client.force_authenticate(user=self.user1)    
        response = self.client.post(self.list_collections_url, {"name": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Name cannot be empty or whitespace.", response.data["name"])

    def test_create_whitespace_name(self):
        """
        Ensures that creating a list with only whitespace as name returns a validation error.
        """
        self.client.force_authenticate(user=self.user1)    
        response = self.client.post(self.list_collections_url, {"name": "   "})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Name cannot be empty or whitespace.", response.data["name"])


    def test_authenticated_user_can_see_lists_where_they_are_participant(self):
        """
        Ensures that users can see lists where they are participants, even if not the author.
        """
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
        """
        Verifies that the 'participants' field in the response is a list of integers (user IDs).
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_collections_url)
        list_user1_data = next(
            (l for l in response.data if l["id"] == self.list_user1.id), None
        )
        participants_field = list_user1_data["participants"]

        self.assertIsInstance(participants_field, list)
        self.assertTrue(all(isinstance(p, int) for p in participants_field))


    def test_unauthenticated_users_get_401_unauthorized(self):
        """
        Ensures that unauthenticated users cannot access any list collections (401 Unauthorized).
        """
        response = self.client.get(self.list_collections_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_creating_a_list_automatically_sets_the_logged_in_user_as_the_author(self):
        """
        Ensures that the logged-in user is automatically set as author when creating a list.
        """
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
        """
         Ensures that the author can delete their own list successfully.
        """
        self.client.force_authenticate(user=self.user1)
        url = reverse("listcollection-detail", args=[self.list_user1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ListCollection.objects.filter(id=self.list_user1.id).exists())


    def test_non_author_cannot_delete_list(self):
        """
        Ensures that non-authors cannot delete lists they do not own.
        """
        self.client.force_authenticate(user=self.user2)
        url = reverse("listcollection-detail", args=[self.list_user1.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can delete this list.")
        self.assertTrue(ListCollection.objects.filter(id=self.list_user1.id).exists())


    def test_updated_at_changes_on_save(self):
        """
        Ensures that 'updated_at' is automatically updated when saving the model.
        """
        collection = ListCollection.objects.create(name="My List", author=self.user1)
        old_updated_at = collection.updated_at
        time.sleep(1)
        collection.name = "Updated List"
        collection.save()

        self.assertNotEqual(collection.updated_at, old_updated_at)
        self.assertGreater(collection.updated_at, old_updated_at)


    def test_author_is_read_only(self):
        """
        Ensures that the 'author' field is read-only and always set to the logged-in user, 
        even if another author is provided in the request.
        """
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post(
            self.list_collections_url,
            {"name": "Testliste", "author": self.user2.id},  # Versuch, anderen Author zu setzen
            format="json"
        )
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["author"], self.user1.id)

class ListCollectionParticipantsLeaveTests(BaseListCollectionSetup):

    def test_participants_can_successfully_leave_the_list(self):
        """
        Ensures that participants can leave a list successfully
        """      
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.leave_url_list_user1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "You have left the list.")


    def test_author_cannot_leave_the_list(self):
        """
        Ensures that the author cannot leave their own list (not considered a participant).
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.leave_url_list_user1)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "You are not a participant of this list.")


class ListCollectionAuthorAddParticipantsTests(BaseListCollectionSetup):

    def test_author_can_add_participants(self):
        """
        Ensures that the author can add a participant to the list.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Participant added successfully.")


    def test_participant_already_added(self):
        """
        Ensures that adding a user who is already a participant returns an error.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is already a participant.")


    def test_adding_a_non_existent_user(self):
        """
        Ensures that adding a non-existent user returns a 404 error.
        """        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 5})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "User does not exist.")


    def test_only_author_can_add_participants(self):
        """
        Ensures that only the author can add participants to a list.
        """
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can add participants.")


    def test_author_cannot_added_to_participants(self):
        """
        Ensures that the author cannot be added as a participant to their own list.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.add_url_list_user1, {"user_id" : 1})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "Author is already the owner of this list.")

class ListCollectionAuthorRemoveParticipantsTests(BaseListCollectionSetup):

    def test_only_author_can_remove_participants(self):
        """
        Ensures that only the author can remove participants from the list.
        """
        self.client.force_authenticate(user=self.user4)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Only the author can remove participants.")


    def test_remove_a_non_existent_user(self):
        """
        Ensures that removing a non-existent user returns a 404 error.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 5})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "User does not exist.")


    def test_remove_a_non_participant_user(self):
        """
        Ensures that removing a user who is not a participant returns an error.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 3})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], "User is not a participant.")


    def test_author_can_remove_participants(self):
        """
        Ensures that the author can successfully remove participants from the list.
        """
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.remove_url_list_user1, {"user_id" : 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], "Participant removed successfully.")


    def test_created_at_and_updated_at_are_set_automatically(self):
        """
        Ensures that 'created_at' and 'updated_at' are automatically set when the list is created.
        """
        collection = ListCollection.objects.create(name="My List", author=self.user1)

        self.assertIsNotNone(collection.created_at)
        self.assertIsNotNone(collection.updated_at)
        self.assertLessEqual(collection.created_at, timezone.now())
        self.assertLessEqual(collection.updated_at, timezone.now())
        delta = abs((collection.updated_at - collection.created_at).total_seconds())
        self.assertLess(delta, 1, f"created_at and updated_at differ by {delta} seconds")