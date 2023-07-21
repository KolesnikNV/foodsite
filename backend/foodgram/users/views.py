from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from djoser import utils
from djoser.views import TokenDestroyView
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from api.serializers import SubscriptionSerializer

from .models import Follow, User

ERROR_SUBSCRIBE_SELF = "Нельзя подписаться на себя"
ERROR_ALREADY_SUBSCRIBED = "Вы уже подписаны на данного автора"
ERROR_NOT_SUBSCRIBED = "Вы не подписаны на данного автора"


class FollowAuthorView(ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def subscribe(self, request, pk):
        """
        Подписка на автора.
        """
        user = request.user
        author = get_object_or_404(User, pk=pk)

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

        follows = User.objects.filter(username=author)
        serializer = SubscriptionSerializer(
            follows, context={"request": request}, many=True
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"])
    def unsubscribe(self, request, pk):
        """
        Отписка от автора.
        """
        user = request.user
        author = get_object_or_404(User, pk=pk)

        subscriptions = Follow.objects.filter(user=user, author=author)

        if not subscriptions.exists():
            return Response(
                {"errors": ERROR_NOT_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        num_deleted, _ = subscriptions.delete()
        if num_deleted == 0:
            return Response(
                {"errors": ERROR_NOT_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
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
    permission_class = (IsAuthenticated,)
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
