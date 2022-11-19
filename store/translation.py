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


class AttributDetailsTranslationOptions(TranslationOptions):
    fields = ('value',)


class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


class ShippingCompanyTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Attribut, AttributTranslationOptions)
translator.register(AttributDetails, AttributDetailsTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(Product, ProductTranslationOptions)
translator.register(ShippingCompany, ShippingCompanyTranslationOptions)
