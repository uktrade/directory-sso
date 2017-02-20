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
