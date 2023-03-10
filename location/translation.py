from modeltranslation.translator import translator, TranslationOptions
from .models import (
    Governorate,
    City, Address
)


class GovernorateTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


class AddressTranslationOptions(TranslationOptions):
    fields = ('address',)
    required_languages = ('en', 'ar')


class CityTranslationOptions(TranslationOptions):
    fields = ('title',)
    required_languages = ('en', 'ar')


translator.register(City, CityTranslationOptions)
translator.register(Governorate, GovernorateTranslationOptions)
translator.register(Address, AddressTranslationOptions)
