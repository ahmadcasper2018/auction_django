from modeltranslation.translator import translator, TranslationOptions

from general.models import KeyWord, Question
from .models import (
    Attribut,
    AttributDetails,
    Category,
    Product,
    ShippingCompany,
    ProductAttribut,
    Brand, SliderMedia, Slider, AttributValue, Page
)


class AttributTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


class AttributDetailsTranslationOptions(TranslationOptions):
    fields = ('value',)
    required_languages = ('en', 'ar')


class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('en', 'ar')


class ShippingCompanyTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en', 'ar')


class BrandTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


class SliderTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('en', 'ar')


class AttributValueTranslationOptions(TranslationOptions):
    fields = ('value',)
    required_languages = ('en', 'ar')


class PageTranslationOptions(TranslationOptions):
    fields = ('about',)
    required_languages = ('en', 'ar')


class KeyWordTranslationOptions(TranslationOptions):
    fields = ('keyword',)
    required_languages = ('en', 'ar')


class QuestionTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')
    required_languages = ('en', 'ar')


translator.register(Attribut, AttributTranslationOptions)
translator.register(AttributDetails, AttributDetailsTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(ShippingCompany, ShippingCompanyTranslationOptions)
translator.register(Brand, BrandTranslationOptions)
translator.register(Slider, SliderTranslationOptions)
translator.register(AttributValue, AttributValueTranslationOptions)
translator.register(Page, PageTranslationOptions)
translator.register(KeyWord, KeyWordTranslationOptions)
translator.register(Question, QuestionTranslationOptions)
