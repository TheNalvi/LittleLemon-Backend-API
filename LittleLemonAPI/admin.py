from django.contrib import admin
from .models import MenuItem, Category
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(Category)
admin.site.register(MenuItem)
