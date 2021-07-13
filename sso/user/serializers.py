from django.contrib.auth import password_validation
from django.db import transaction
from rest_framework import serializers

from sso.user import utils
from sso.user.models import User, UserAnswer, UserProfile
from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = (
            'code',
            'expiration_date',
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


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    social_account = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            'first_name',
            'last_name',
            'job_title',
            'mobile_phone_number',
            'segment',
            'profile_image',
            'social_account',
        )

    def get_profile_image(self, obj):
        account = obj.user.socialaccount_set.first()
        if account:
            return utils.get_social_account_image(account)

    def get_social_account(self, obj):
        account = obj.user.socialaccount_set.first()
        return account.provider if account else 'email'

    def to_internal_value(self, data):
        return {**data, 'user_id': self.context['request'].user.pk}


class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer()
    social_login = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'hashed_uuid',
            'social_login',
            'user_profile',
        )

    def get_social_login(self, obj):
        return bool(obj.socialaccount_set.all())


class ActivityStreamUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'date_joined', 'modified')


class ActivityStreamUserAnswerSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='question.title')
    answer_label = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = ('id', 'user_id', 'answer', 'modified', 'question_id', 'question_title', 'answer_label')

    def get_answer_label(self, obj):
        if obj.question.question_type in ['MULTI_SELECT', 'SELECT', 'RADIO']:
            return (
                self.get_choice_value(
                    obj.answer,
                    obj.question.to_dict()['choices'],
                )
                or ''
            )

    def get_choice_value(self, value, choices_array):
        choices_list = choices_array if isinstance(choices_array, list) else choices_array.get('options', choices_array)
        for c in choices_list:
            if c.get('value') == value:
                return c.get('label')
