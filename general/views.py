from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from general.models import Question, KeyWord, ContactSettings
from general.serializers import (
    QuestionSerializer,
    KeywordSerializer,
    ContactSettingsSerializer
)
from .permessions import SettingsAccress


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    permission_classes = (SettingsAccress,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class KeyWordViewSet(viewsets.ModelViewSet):
    queryset = KeyWord.objects.all()
    serializer_class = KeywordSerializer

    permission_classes = (SettingsAccress,)


class ContactSettingsViewSet(mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             viewsets.GenericViewSet):
    queryset = ContactSettings.objects.all()
    serializer_class = ContactSettingsSerializer
    permission_classes = (SettingsAccress,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response([serializer.data])
