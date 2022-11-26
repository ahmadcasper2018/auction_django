from abc import ABC

from rest_framework import serializers
from .models import Question, KeyWord


class KeywordSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    keyword = serializers.CharField(max_length=128)


class QuestionSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(many=True)

    def create(self, validated_data):
        keywords = validated_data.pop('keyword')
        instance = super(QuestionSerializer, self).create(validated_data)
        for key in keywords:
            new_keyword, create = KeyWord.objects.get_or_create(**key)
            instance.keyword.add(new_keyword)
        return instance

    class Meta:
        model = Question
        fields = ('id', 'question', 'answer', 'keyword')
