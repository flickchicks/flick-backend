from lst.serializers import LstWithSimpleShowsSerializer
from rest_framework import serializers
from show.simple_serializers import ShowSimpleSerializer

from .models import DiscoverRecommendation


class DiscoverRecommendationSerializer(serializers.ModelSerializer):

    lst = LstWithSimpleShowsSerializer(many=False)
    show = ShowSimpleSerializer(many=False)

    class Meta:
        model = DiscoverRecommendation
        fields = ("recommend_type", "lst", "show")
        ready_only_fields = fields
