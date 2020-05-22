from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

# from user.models import User
from .models import Item
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 
            'username',
            'email',
        )
        read_only_fields = ('id',)

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
