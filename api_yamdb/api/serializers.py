from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title, User


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объекта класса Review."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        title = get_object_or_404(Title, pk=title_id)
        user = self.context['request'].user
        if (
            self.context['request'].method == 'POST'
            and Review.objects.filter(author=user, title=title).exists()
        ):
            raise ValidationError(
                'На одно произведение иожно оставить один отзыв.'
            )
        return data

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для создания объекта класса Comment."""

    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('review',)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Genre
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        read_only=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class UserCreateSerializer(serializers.Serializer):
    """Сериализатор для создания объекта класса User."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(required=True, max_length=128)

    class Meta:
        fields = (
            'username', 'email'
        )

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        return user

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено'
            )
        if User.objects.filter(
                username=data.get('username'),
                email=data.get('email'),
        ).exists():
            return data

        username_exists = User.objects.filter(
            username=data.get('username'),
        ).exists()
        email_exists = User.objects.filter(email=data.get('email')).exists()

        if username_exists and email_exists:
            return data

        if username_exists:
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )

        if email_exists:
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data


class UserRecieveTokenSerializer(serializers.Serializer):
    """Сериализатор для объекта класса User при получении токена JWT."""

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role'
        )

    def validate_username(self, username):
        if username in 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" запрещено'
            )
        return username
