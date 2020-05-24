from django.contrib.auth.models import User

# from rest_framework.fields import CurrentUserDefault
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField, HiddenField

from .models import Item
from user.serializers import UserSerializer

class CurrentUserDefault(object):
    def set_context(self, serializer_field):
        self.user_id = serializer_field.context['request'].user.id

    def __call__(self):
        return self.user_id

    def __repr__(self):
        return unicode_to_repr('%s()' % self.__class__.__name__)

class ItemSerializer(ModelSerializer):

    """
    Item Detail Serializer
    """

    # owner = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    
    # owner = PrimaryKeyRelatedField(default=CurrentUserDefault(), read_only=True)
    owner_id = HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Item
        fields = (
            'id',
            'asset_bundle',
            'owner_id',
            'created_at',
        )
        read_only_fields = ('id',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ItemDetailSerializer(ModelSerializer):
    owner = UserSerializer(many=False, read_only=True)
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
        

