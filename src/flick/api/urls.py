from django.urls import include, path

from rest_framework import routers

from item.views import ItemList, ItemDetail
from user.views import UserViewSet
from asset.views import AssetBundleList, AssetBundleDetail

from flick_auth import urls as auth_urls

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('items/', ItemList.as_view(), name='item-list'),
    path('items/<int:pk>/', ItemDetail.as_view(), name='item-detail'),

    path('asset-bundles/', AssetBundleList.as_view(), name='asset-bundles-list'),
    path('asset-bundles/<int:pk>/', AssetBundleDetail.as_view(), name='asset-bundles-detail'),

    path('auth/', include(auth_urls)),

    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]