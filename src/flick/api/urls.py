from asset.views import AssetBundleDetail, AssetBundleList
from django.urls import include, path
from flick_auth import urls as auth_urls
from item.views import CommentItem, ItemDetail, ItemList, LikeItem
from rest_framework import routers
from upload.views import UploadImage
from user.views import UserViewSet

from friend.views import (
    FriendList,
    FriendRequestListAndCreate,
    FriendAcceptListAndCreate,
    FriendRejectListAndCreate,
    FriendRemoveListAndCreate,
)
from discover.views import DiscoverShow
from search.views import Search
from lst.views import LstList, LstDetail
from show.views import ShowViewSet
from tag.views import TagList, TagDetail

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"shows", ShowViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("asset-bundles/", AssetBundleList.as_view(), name="asset-bundles-list"),
    path("asset-bundles/<int:pk>/", AssetBundleDetail.as_view(), name="asset-bundles-detail"),
    path("auth/", include(auth_urls)),
    path("comment/", CommentItem.as_view(), name="comment"),
    path("discover/show/", DiscoverShow.as_view(), name="discover-show"),
    path("friendship/", include("friendship.urls")),
    path("friends/", FriendList.as_view(), name="friend-list"),
    path("friends/request/", FriendRequestListAndCreate.as_view(), name="friend-request"),
    path("friends/accept/", FriendAcceptListAndCreate.as_view(), name="friend-accept"),
    path("friends/reject/", FriendRejectListAndCreate.as_view(), name="friend-reject"),
    path("friends/remove/", FriendRemoveListAndCreate.as_view(), name="friend-remove"),
    path("items/", ItemList.as_view(), name="item-list"),
    path("items/<int:pk>/", ItemDetail.as_view(), name="item-detail"),
    path("like/", LikeItem.as_view(), name="like"),
    path("lsts/", LstList.as_view(), name="item-list"),
    path("lsts/<int:pk>/", LstDetail.as_view(), name="item-detail"),
    path("media/image/", UploadImage.as_view(), name="upload"),
    path("search/", Search.as_view(), name="search-show"),
    path("tags/", TagList.as_view(), name="tag-list"),
    path("tags/<int:pk>/", TagDetail.as_view(), name="tag-detail"),
]
