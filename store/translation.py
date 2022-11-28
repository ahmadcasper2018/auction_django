from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Attribut,
    AttributDetails,
    Category,
    Product,
    ShippingCompany,
)


class AttributTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


class AttributDetailsTranslationOptions(TranslationOptions):
    fields = ('value',)
    required_languages = ('en', 'ar')


# class CategoryTranslationOptions(TranslationOptions):
#     fields = ('title',)
#     required_languages = ('en', 'ar')


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
    required_languages = ('en', 'ar')


class ShippingCompanyTranslationOptions(TranslationOptions):
    fields = ('name',)
    required_languages = ('en', 'ar')


translator.register(Attribut, AttributTranslationOptions)
translator.register(AttributDetails, AttributDetailsTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(ShippingCompany, ShippingCompanyTranslationOptions)
