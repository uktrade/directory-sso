from django.db import transaction
from rest_framework import serializers


from sso.user.models import User, UserProfile
from sso.verification.models import VerificationCode


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


class CreateUserSerializer(serializers.ModelSerializer):
    verification_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'password',
            'verification_code',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'verification_code': {'read_only': True}
        }

    @transaction.atomic
    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        instance.verificationcode = VerificationCode.objects.create(
            user=instance
        )
        return instance

    def get_verification_code(self, instance):
        return instance.verificationcode.code


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
        data['user_id'] = self.context['request'].user.pk
        return data
