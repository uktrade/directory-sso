from rest_framework import serializers

from sso.user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'email',
        )


class LastLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = (
            'id',
            'last_login',
        )


class PasswordCheckSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'})
    session_key = serializers.CharField(style={'input_type': 'password'})
