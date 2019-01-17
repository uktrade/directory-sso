from rest_framework import serializers

from sso.verification.models import VerificationCode


class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = []

    def to_internal_value(self, data):
        data['user'] = self.context['request'].user
        return data
