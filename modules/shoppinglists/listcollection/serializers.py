from rest_framework import serializers
from .models import ListCollection

class ListCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListCollection
        fields = ["id", "name", "author", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]

class ParticipantActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def validate_user_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invalid user id.")
        return value