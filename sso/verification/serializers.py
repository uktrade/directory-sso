from rest_framework import serializers

from django.utils.crypto import constant_time_compare

from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = []

    def to_internal_value(self, data):
        if 'request' in self.context.keys():
            data['user_id'] = self.context['request'].user.pk
        return data


class CheckVerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5, min_length=5)

    def validate_code(self, value):
        verification_code = self.context['verificationcode']

        if verification_code.is_expired:
            raise serializers.ValidationError(
                "Registration verification code expired"
            )

        if not constant_time_compare(value, verification_code.code):
            raise serializers.ValidationError(
                "Invalid registration verification code"
            )
