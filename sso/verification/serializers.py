from rest_framework import serializers

from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = []

    def to_internal_value(self, data):
        if 'request' in self.context.keys():
            data['user_id'] = self.context['request'].user.pk
        return data

    def validate_code(self, value):
        if value != self.context['expected_code']:
            raise serializers.ValidationError(
                "Invalid registration verification code"
            )
