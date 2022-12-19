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

    # permission_classes = (IsStaff,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
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
