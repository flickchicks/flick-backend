from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from .models import AssetBundle
from user.serializers import UserSerializer

class AssetBundleSerializer(ModelSerializer):

    owner = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = AssetBundle
        fields = (
            'id', 
            'salt', 
            'kind', 
            'base_url',
            'owner',
            'created_at',
        )
        read_only_fields = ('id',)

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
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id',)