from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from .mixins import ModelMixinSet
from .permissions import (AnonimReadOnly, IsAdmin,
                          IsSuperUserIsAdminIsModeratorIsAuthor)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UserCreateSerializer, UserRecieveTokenSerializer,
                          UserSerializer)
from api.filters import TitleFilter
from api_yamdb.settings import DOMAIN_NAME
from reviews.models import Category, Genre, Review, Title, User

EMAIL_YAMDB = f'admin@{DOMAIN_NAME}'


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsSuperUserIsAdminIsModeratorIsAuthor,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.review.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsSuperUserIsAdminIsModeratorIsAuthor]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'
    permission_classes = (AnonimReadOnly | IsAdmin,)


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AnonimReadOnly | IsAdmin,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('review__score')
    ).all()
    permission_classes = (AnonimReadOnly | IsAdmin,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


def send_confirmation_code(email, confirmation_code):
    """Oтправляет на почту пользователя код подтверждения."""
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=EMAIL_YAMDB,
        recipient_list=(email,),
        fail_silently=False,
    )


class UserCreateView(APIView):
    """Cоздаёт обьекты класса User."""

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Создает объект класса User и
        отправляет на почту пользователя код подтверждения."""

        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(
            email=user.email,
            confirmation_code=confirmation_code
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserReceiveTokenViewSet(mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    """Пользователь получает JWT токен."""

    queryset = User.objects.all()
    serializer_class = UserRecieveTokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = UserRecieveTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Неверный код подтверждения'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user'
    )
    def get_user_by_username(self, request, username):
        """Получание данных пользователя по его username и
        управление данными"""

        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me_data(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
