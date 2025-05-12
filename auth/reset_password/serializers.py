from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
class SendResetPasswordMailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordIfLoggedInSerializer(serializers.Serializer):
    password_old = serializers.CharField(write_only=True)
    password_new = serializers.CharField(write_only=True)
    password_new_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password_new'] != data['password_new_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data