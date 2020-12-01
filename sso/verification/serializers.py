from django.utils.crypto import constant_time_compare
from rest_framework import serializers

from sso.verification.models import VerificationCode


class RegenerateCodeSerializer(serializers.ModelSerializer):
    MESSAGE_CODE_VERIFIED = 'User is already verified'

    class Meta:
        model = VerificationCode
        fields = ['code', 'expiration_date']

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
