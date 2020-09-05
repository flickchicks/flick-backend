from user.views import UserViewSet

from asset.views import AssetBundleDetail
from asset.views import AssetBundleList
from discover.views import DiscoverShow
from django.urls import include
from django.urls import path
from flick_auth import urls as auth_urls
from flick_auth.views import AuthenticateView
from flick_auth.views import UserProfileView
from flick_auth.views import UserView
from friend.views import FriendAcceptListAndCreate
from friend.views import FriendList
from friend.views import FriendRejectListAndCreate
from friend.views import FriendRemoveListAndCreate
from friend.views import FriendRequestListAndCreate
from like.views import LikeView
from lst.views import LstDetail
from lst.views import LstDetailAdd
from lst.views import LstDetailRemove
from lst.views import LstList
from notification.views import NotificationList
from read.views import ReadView
from rest_framework import routers
from search.views import Search
from show.views import ShowDetail
from show.views import ShowViewSet
from suggestion.views import PrivateSuggestionView
from tag.views import TagDetail
from tag.views import TagList
from upload.views import UploadImage

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"shows", ShowViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("asset-bundles/", AssetBundleList.as_view(), name="asset-bundles-list"),
    path("asset-bundles/<int:pk>/", AssetBundleDetail.as_view(), name="asset-bundles-detail"),
    path("me/", UserView.as_view(), name="me"),
    path("user/<int:pk>", UserProfileView.as_view(), name="user-profile"),
    path("authenticate/", AuthenticateView.as_view(), name="authenticate"),
    path("auth/", include(auth_urls)),
    path("comment/<int:pk>/like/", LikeView.as_view(), name="like-comment"),
    path("comment/<int:pk>/read/", ReadView.as_view(), name="read-comment"),
    path("discover/show/", DiscoverShow.as_view(), name="discover-show"),
    path("friendship/", include("friendship.urls")),
    path("friends/", FriendList.as_view(), name="friend-list"),
    path("friends/request/", FriendRequestListAndCreate.as_view(), name="friend-request"),
    path("friends/accept/", FriendAcceptListAndCreate.as_view(), name="friend-accept"),
    path("friends/reject/", FriendRejectListAndCreate.as_view(), name="friend-reject"),
    path("friends/remove/", FriendRemoveListAndCreate.as_view(), name="friend-remove"),
    path("lsts/", LstList.as_view(), name="lst-list"),
    path("lsts/<int:pk>/", LstDetail.as_view(), name="lst-detail"),
    path("lsts/<int:pk>/add/", LstDetailAdd.as_view(), name="lst-detail-add"),
    path("lsts/<int:pk>/remove/", LstDetailRemove.as_view(), name="lst-detail-remove"),
    path("media/image/", UploadImage.as_view(), name="upload"),
    path("search/", Search.as_view(), name="search"),
    path("tags/", TagList.as_view(), name="tag-list"),
    path("tags/<int:pk>/", TagDetail.as_view(), name="tag-detail"),
    path("show/<int:pk>/", ShowDetail.as_view(), name="show-detail"),
    path("suggest/", PrivateSuggestionView.as_view(), name="private-suggestion"),
    path("notifications/", NotificationList.as_view(), name="notif-list"),
]
