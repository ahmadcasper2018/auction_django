from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Governorate,
    City
)


class GovernorateTranslationOptions(TranslationOptions):
    fields = ('title',)


class CityTranslationOptions(TranslationOptions):
    fields = ('title',)


translator.register(City, CityTranslationOptions)
translator.register(Governorate, GovernorateTranslationOptions)
