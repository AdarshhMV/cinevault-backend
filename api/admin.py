from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Movie

# This line puts the table on your admin dashboard
admin.site.register(Movie)