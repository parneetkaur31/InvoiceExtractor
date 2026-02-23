from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Invoice, ExtractionRule

admin.site.register(Invoice)
admin.site.register(ExtractionRule)
