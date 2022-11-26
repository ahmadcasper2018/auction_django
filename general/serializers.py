from rest_framework import serializers
from .models import Question, KeyWord


class KeywordSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'keyword')


class QuestionSerializer(serializers.ModelSerializer):
    keywords = KeywordSerializer(many=True, read_only=True)

    def create(self, validated_data):
        keywords = validated_data.pop('keywords')
        instance = super(QuestionSerializer, self).create(validated_data)
        for key in keywords:
            KeyWord.objects.create(question=instance, **key)
        return instance

    class Meta:
        model = Question
        fields = ('id', 'question', 'answer', 'keywords')
