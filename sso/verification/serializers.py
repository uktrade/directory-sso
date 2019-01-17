from rest_framework import serializers

from sso.verification.models import Validation


class ValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validation

        fields = (
            'id',
            'code',
            'user',
        )

    def create(self, validated_data):

        return super().create(validated_data)

    def to_internal_value(self, data):
        data['user'] = self.context['request'].user
        return data
