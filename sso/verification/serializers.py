from rest_framework import serializers

from django.utils.crypto import constant_time_compare

from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = []

    def to_internal_value(self, data):
        data['user_id'] = self.context['request'].user.pk
        return data


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
