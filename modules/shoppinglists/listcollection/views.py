from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ListCollection
from .serializers import ListCollectionSerializer


class ListCollectionView(viewsets.ModelViewSet):
    queryset = ListCollection.objects.all()
    serializer_class = ListCollectionSerializer
    permission_classes = [IsAuthenticated]  # Nur authentifizierte User dürfen darauf zugreifen

    def get_queryset(self):
        return ListCollection.objects.filter(author=self.request.user)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)