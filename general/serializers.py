from abc import ABC

from rest_framework import serializers

from store.serializers import SliderSerializer
from .models import Question, KeyWord, ContactSettings


class KeywordSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    keyword = serializers.SerializerMethodField()
    keyword_current = serializers.CharField(read_only=True, source='keyword')
    keyword_en = serializers.CharField(write_only=True)
    keyword_ar = serializers.CharField(write_only=True)

    def get_keyword(self, instance):
        return {
            'en': instance.keyword_en,
            'ar': instance.keyword_ar,
        }

    class Meta:
        model = KeyWord
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    keyword = KeywordSerializer(many=True, read_only=True)
    question = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    question_current = serializers.CharField(source='question', read_only=True)
    answer_current = serializers.CharField(source='answer', read_only=True)
    question_en = serializers.CharField(write_only=True)
    question_ar = serializers.CharField(write_only=True)

    answer_en = serializers.CharField(write_only=True)
    answer_ar = serializers.CharField(write_only=True)

    def get_question(self, instance):
        return {
            'en': instance.question_en,
            'ar': instance.question_ar
        }

    def get_answer(self, instance):
        return {
            'en': instance.answer_en,
            'ar': instance.answer_ar
        }

    def create(self, validated_data):
        keywords = self.context['request'].data.get('keywords')
        instance = super(QuestionSerializer, self).create(validated_data)
        for key in keywords:
            new_keyword, created = KeyWord.objects.get_or_create(pk=key)
            instance.keyword.add(new_keyword)
        return instance

    class Meta:
        model = Question
        fields = '__all__'


class ContactSettingsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactSettings
        fields = '__all__'
