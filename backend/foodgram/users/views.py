from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.serializers import TokenCreateSerializer
from djoser.views import TokenDestroyView
from rest_framework import filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Follow, User
from .serializers import SubscriptionSerializer

ERROR_SUBSCRIBE_SELF = "Нельзя подписаться на себя"
ERROR_ALREADY_SUBSCRIBED = "Вы уже подписаны на данного автора"
ERROR_NOT_SUBSCRIBED = "Вы не подписаны на данного автора"


class CustomTokenCreateSerializer(TokenCreateSerializer):
    """
    Пользовательский сериализатор для создания токена аутентификации.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username")


@api_view(["POST", "DELETE"])
@permission_classes([IsAuthenticated])
def follow_author(request, pk):
    """
    Подписка на автора.
    """

    user = get_object_or_404(User, username=request.user.username)
    author = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        if user.id == author.id:
            return Response(
                {"errors": ERROR_SUBSCRIBE_SELF},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            Follow.objects.create(user=user, author=author)
        except IntegrityError:
            return Response(
                {"errors": ERROR_ALREADY_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        follows = User.objects.all().filter(username=author)
        serializer = SubscriptionSerializer(
            follows, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    if request.method == "DELETE":
        try:
            subscription = Follow.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            return Response(
                {"errors": ERROR_NOT_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return HttpResponse(
            "Вы успешно отписаны от этого автора",
            status=status.HTTP_204_NO_CONTENT,
        )


class SubscriptionListView(ReadOnlyModelViewSet):
    """
    ViewSet для генерации списка подписок пользователя.
    """

    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAuthenticated,)
    search_fields = ("^following__user",)

    def get_queryset(self):
        user = self.request.user
        new_queryset = User.objects.filter(following__user=user)
        return new_queryset


class CustomTokenDestroyView(TokenDestroyView):
    """
    Пользовательский класс для удаления токена аутентификации.
    """

    def post(self, request):
        utils.logout_user(request)
        return Response(status=status.HTTP_201_CREATED)
