from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from .models import Item
from user.serializers import UserSerializer

class ItemSerializer(ModelSerializer):
    owner = PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Item
        fields = (
            'id', 'title', 'subtitle', 'owner',
        )
        read_only_fields = ('id',) # need comma, only accepts tuple!

class ItemDetailSerializer(ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Item
        fields = (
            'id', 
            'title',
            'subtitle',
            'owner',
            'create_at',
            'updated_at',
        )
        read_only_fields = ('id',)
