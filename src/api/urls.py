from user.views import UserViewSet

from asset.views import AssetBundleDetail
from asset.views import AssetBundleList
from discover.views import DiscoverView
from django.urls import include
from django.urls import path
from flick_auth.async_views import index
from flick_auth.views import AuthenticateView
from flick_auth.views import CheckUsernameView
from flick_auth.views import LogoutView
from flick_auth.views import UserProfileView
from flick_auth.views import UserView
from friend.views import FriendAcceptListAndCreate
from friend.views import FriendList
from friend.views import FriendRejectListAndCreate
from friend.views import FriendRemoveListAndCreate
from friend.views import FriendRequestListAndCreate
from friend.views import UserFriendList
from group.views import GroupClearShows
from group.views import GroupDetail
from group.views import GroupDetailAdd
from group.views import GroupDetailRemove
from group.views import GroupList
from group.views import GroupPendingList
from group.views import GroupShowList
from group.views import GroupVoteShow
from like.views import LikeView
from like.views import LstLikeView
from like.views import SuggestionLikeView
from lst.views import LstDetail
from lst.views import LstDetailAdd
from lst.views import LstDetailRemove
from lst.views import LstList
from notification.views import NotificationEnable
from notification.views import NotificationList
from notification.views import NotificationTest
from read.views import ReadView
from recommend.views import LstRecommendView
from rest_framework import routers
from search.views import Search
from show.views import AddShowToListsView
from show.views import ShowDetail
from show.views import ShowViewSet
from suggestion.views import CreateSuggestion
from suggestion.views import SuggestionList
from tag.views import TagDetail
from tag.views import TagList
from upload.views import UploadImage

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"shows", ShowViewSet)

urlpatterns = [
    path("async/", index, name="async"),
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("asset-bundles/", AssetBundleList.as_view(), name="asset-bundles-list"),
    path("asset-bundles/<int:pk>/", AssetBundleDetail.as_view(), name="asset-bundles-detail"),
    path("authenticate/", AuthenticateView.as_view(), name="authenticate"),
    path("comment/<int:pk>/like/", LikeView.as_view(), name="like-comment"),
    path("comment/<int:pk>/read/", ReadView.as_view(), name="read-comment"),
    path("discover/", DiscoverView.as_view(), name="discover"),
    path("friendship/", include("friendship.urls")),
    path("friends/", FriendList.as_view(), name="friend-list"),
    path("friends/request/", FriendRequestListAndCreate.as_view(), name="friend-request"),
    path("friends/accept/", FriendAcceptListAndCreate.as_view(), name="friend-accept"),
    path("friends/reject/", FriendRejectListAndCreate.as_view(), name="friend-reject"),
    path("friends/remove/", FriendRemoveListAndCreate.as_view(), name="friend-remove"),
    path("groups/", GroupList.as_view(), name="group-list"),
    path("groups/<int:pk>/", GroupDetail.as_view(), name="group-detail"),
    path("groups/<int:pk>/add/", GroupDetailAdd.as_view(), name="group-detail-add"),
    path("groups/<int:pk>/remove/", GroupDetailRemove.as_view(), name="group-detail-remove"),
    path("groups/<int:pk>/pending/", GroupPendingList.as_view(), name="group-pending-list"),
    path("groups/<int:pk>/shows/", GroupShowList.as_view(), name="group-show-list"),
    path("groups/<int:pk>/shows/clear/", GroupClearShows.as_view(), name="group-clear-shows"),
    path("groups/<int:group_pk>/shows/<int:show_pk>/vote/", GroupVoteShow.as_view(), name="group-vote-show"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("lsts/", LstList.as_view(), name="lst-list"),
    path("lsts/<int:pk>/", LstDetail.as_view(), name="lst-detail"),
    path("lsts/<int:pk>/add/", LstDetailAdd.as_view(), name="lst-detail-add"),
    path("lsts/<int:pk>/recommend/", LstRecommendView.as_view(), name="lst-recommend"),
    path("lsts/<int:pk>/remove/", LstDetailRemove.as_view(), name="lst-detail-remove"),
    path("lsts/<int:pk>/like/", LstLikeView.as_view(), name="like-list"),
    path("me/", UserView.as_view(), name="me"),
    path("media/image/", UploadImage.as_view(), name="upload"),
    path("search/", Search.as_view(), name="search"),
    path("show/<int:pk>/", ShowDetail.as_view(), name="show-detail"),
    path("show/<int:pk>/lsts/add/", AddShowToListsView.as_view(), name="add-show-to-list"),
    path("suggest/", CreateSuggestion.as_view(), name="private-suggestion"),
    path("suggestions/", SuggestionList.as_view(), name="private-suggestion-list"),
    path("suggestions/<int:pk>/like/", SuggestionLikeView.as_view(), name="like-private-suggestion"),
    path("tags/", TagList.as_view(), name="tag-list"),
    path("tags/<int:pk>/", TagDetail.as_view(), name="tag-detail"),
    path("user/<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("user/<int:pk>/friends/", UserFriendList.as_view(), name="user-friend-lists"),
    path("username/", CheckUsernameView.as_view(), name="check-username"),
    path("notifications/", NotificationList.as_view(), name="notif-list"),
    path("notifications/enable/", NotificationEnable.as_view(), name="notif-enable"),
    path("notiftest/", NotificationTest.as_view(), name="notif-test"),
]
