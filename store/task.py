from .models import Product

target = Product.objects.last()
target.title_en = 'cron is working fine '
target.save()
