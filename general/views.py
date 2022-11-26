from django.shortcuts import render
from rest_framework import viewsets
# Create your views here.
from general.models import Question
from general.serializers import QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
