from django.urls import include, path
from rest_framework import routers

from .views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet, UserCreateView,
                    UserReceiveTokenViewSet, UserViewSet)

router = routers.DefaultRouter()
router.register(
    'titles/(?P<title_id>\\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
),
router.register(
    'titles/(?P<title_id>\\d+)/reviews/(?P<review_id>\\d+)/comments',
    CommentViewSet,
    basename='comments'
),
router.register('users', UserViewSet, basename='users')
router.register('categories', CategoryViewSet, basename='categoty')
router.register('genres', GenreViewSet, basename='genre')
router.register('titles', TitleViewSet, basename='title')

auth_urls = [
    path(
        'signup/',
        UserCreateView.as_view(),
        name='signup'
    ),
    path(
        'token/',
        UserReceiveTokenViewSet.as_view({'post': 'create'}),
        name='token'
    )
]

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/', include(auth_urls)),
]
