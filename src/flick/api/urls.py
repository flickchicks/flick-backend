from asset.views import AssetBundleDetail, AssetBundleList
from django.urls import include, path
from flick_auth import urls as auth_urls
from item.views import CommentItem, ItemDetail, ItemList, LikeItem
from rest_framework import routers
from upload.views import UploadImage
from user.views import UserViewSet

from show.views import ShowViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"shows", ShowViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("items/", ItemList.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetail.as_view(), name="item-detail"),
    path("asset-bundles/", AssetBundleList.as_view(), name="asset-bundles-list"),
    path("asset-bundles/<int:pk>/", AssetBundleDetail.as_view(), name="asset-bundles-detail"),
    path("auth/", include(auth_urls)),
    path("media/image/", UploadImage.as_view(), name="upload"),
    path("like/", LikeItem.as_view(), name="like"),
    path("comment/", CommentItem.as_view(), name="comment"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
