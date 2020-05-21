from django.urls import include, path
from rest_framework import routers
from .views import UserViewSet, item_list

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(r'api/items', item_list)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('items/', item_list),
    path('items/<int:pk>/', item_list),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]