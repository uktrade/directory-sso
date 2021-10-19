from django.utils.crypto import constant_time_compare
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers

from sso.verification import helpers
from sso.verification.models import VerificationCode


class RegenerateCodeSerializer(serializers.ModelSerializer):
    MESSAGE_CODE_VERIFIED = 'User is already verified'

    user_uidb64 = serializers.SerializerMethodField()
    verification_token = serializers.SerializerMethodField()

    class Meta:
        model = VerificationCode
        fields = ['code', 'expiration_date', 'user_uidb64', 'verification_token']

    def get_user_uidb64(self, obj):
        return urlsafe_base64_encode(force_bytes(obj.user.pk))

    def get_verification_token(self, obj):
        return helpers.verification_token.make_token(obj.user)

    def validate(self, value):
        if self.instance.date_verified is not None:
            raise serializers.ValidationError(self.MESSAGE_CODE_VERIFIED)
        return value


class CheckVerificationCodeSerializer(serializers.ModelSerializer):
    MESSAGE_CODE_EXPIRED = 'Registration verification code expired'
    MESSAGE_CODE_MISMATCH = 'Invalid registration verification code'

    class Meta:
        model = VerificationCode
        fields = ['code']

    def validate_code(self, value):
        if self.instance.is_expired:
            raise serializers.ValidationError(self.MESSAGE_CODE_EXPIRED)
        if not constant_time_compare(value, self.instance.code):
            raise serializers.ValidationError(self.MESSAGE_CODE_MISMATCH)
        return value
