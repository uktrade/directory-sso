from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework import serializers

from django.contrib.auth import password_validation

from sso.user.models import User, UserProfile
from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = VerificationCode
        fields = (
            'code',
            'expiration_date',
        )


class UserSerializer(serializers.ModelSerializer):

    has_user_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'hashed_uuid',
            'has_user_profile',
        )

    def get_has_user_profile(self, obj):
        try:
            obj.userprofile
        except ObjectDoesNotExist:
            return False
        else:
            return True


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


class CreateUserSerializer(serializers.ModelSerializer):
    verification_code = VerificationCodeSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'verification_code',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        VerificationCode.objects.create(user=instance)
        return instance


class CreateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'job_title',
            'mobile_phone_number',
        )

    def to_internal_value(self, data):
        return {**data, 'user_id': self.context['request'].user.pk}
