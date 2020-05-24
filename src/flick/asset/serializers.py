from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault

from .models import AssetBundle
from user.serializers import UserSerializer

class AssetBundleSerializer(ModelSerializer):

    owner = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())

    class Meta:
        model = AssetBundle
        fields = (
            'id', 
            'salt', 
            'kind', 
            'base_url',
            'owner',
            'asset_urls',
            'created_at',
        )
        read_only_fields = ('id',)
        
    def save(self):
        user = CurrentUserDefault()

class AssetBundleDetailSerializer(ModelSerializer):

    owner = UserSerializer(many=False, read_only=True)

    class Meta:
        model = AssetBundle
        fields = (
            'id', 
            'salt', 
            'kind', 
            'base_url',
            'owner',
            'asset_urls',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id',)