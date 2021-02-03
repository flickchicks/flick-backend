from rest_framework import serializers

from .models import Provider


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = (
            "id",
            "name",
            "image",
        )
        read_only_fields = fields
