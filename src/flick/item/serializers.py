from django.contrib.auth.models import User

# from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, CurrentUserDefault

from .models import Item
from user.serializers import UserSerializer
from asset.serializers import AssetBundleDetailSerializer

class ItemSerializer(ModelSerializer):
    # CurrentUserDefault is basically request.data (the authenticated user related to this request)
    owner = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    
    class Meta:
        model = Item
        fields = (
            'id',
            'asset_bundle',
            'owner',
            'created_at',
        )
        read_only_fields = ('id',)

class ItemDetailSerializer(ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    asset_bundle = AssetBundleDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Item
        fields = (
            'id', 
            'asset_bundle',
            'owner',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id',) # need comma, only accepts tuple!
        

