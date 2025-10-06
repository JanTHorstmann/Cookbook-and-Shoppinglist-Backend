from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ListCollection
from .serializers import ListCollectionSerializer, ParticipantActionSerializer
from rest_framework.decorators import action
from django.db import models
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()
class ListCollectionView(viewsets.ModelViewSet):
    queryset = ListCollection.objects.all()
    serializer_class = ListCollectionSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte User dürfen darauf zugreifen

    def get_queryset(self):
        user = self.request.user
        return ListCollection.objects.filter(models.Q(author=user) | models.Q(participants=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.can_delete(request.user):
            return Response({"detail": "Only the author can delete this list."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=["post"], url_path="leave")
    def leave_list(self, request, pk=None):
        """Ermöglicht Teilnehmern, sich selbst zu entfernen."""
        list_obj = self.get_object()
        user = request.user
        if list_obj.can_leave(user):
            list_obj.participants.remove(user)
            return Response({"detail": "You have left the list."})
        return Response({"detail": "You are not a participant of this list."},
                        status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"], url_path="add-participant")
    def add_participant(self, request, pk=None):
        """Nur der Autor darf Teilnehmer hinzufügen."""
        list_obj = self.get_object()
        if request.user != list_obj.author:
            return Response({"detail": "Only the author can add participants."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ParticipantActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]

        # User abrufen
        try:
            user_to_add = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if user_to_add == list_obj.author:
            return Response({"detail": "Author is already the owner of this list."},
                            status=status.HTTP_400_BAD_REQUEST)

        if list_obj.participants.filter(pk=user_to_add.pk).exists():
            return Response({"detail": "User is already a participant."},
                            status=status.HTTP_400_BAD_REQUEST)

        list_obj.participants.add(user_to_add)
        return Response({"detail": "Participant added successfully.",
                         "participant_id": user_to_add.id},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="remove-participant")
    def remove_participant(self, request, pk=None):
        """Nur der Autor darf Teilnehmer entfernen."""
        list_obj = self.get_object()
        if request.user != list_obj.author:
            return Response({"detail": "Only the author can remove participants."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ParticipantActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data["user_id"]

        try:
            user_to_remove = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if not list_obj.participants.filter(pk=user_to_remove.pk).exists():
            return Response({"detail": "User is not a participant."},
                            status=status.HTTP_400_BAD_REQUEST)

        list_obj.participants.remove(user_to_remove)
        return Response({"detail": "Participant removed successfully.",
                         "participant_id": user_to_remove.id},
                        status=status.HTTP_200_OK)
    