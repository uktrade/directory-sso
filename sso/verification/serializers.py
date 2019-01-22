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


class CheckVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5, min_length=5)
    MESSAGE_CODE_EXPIRED = 'Registration verification code expired'
    MESSAGE_CODE_MISMATCH = 'Invalid registration verification code'

    def validate_code(self, value):
        verification_code = self.context['request'].user.verificationcode

        if verification_code.is_expired:
            raise serializers.ValidationError(
                self.MESSAGE_CODE_EXPIRED
            )

        if not constant_time_compare(value, verification_code.code):
            raise serializers.ValidationError(
                self.MESSAGE_CODE_MISMATCH
            )
        return True
