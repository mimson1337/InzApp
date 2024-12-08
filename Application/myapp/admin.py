from django.contrib import admin
# from . models import TodoItem
# Register your models here.

# admin.site.register(TodoItem)
from django.contrib import admin
from .models import AudioFile

admin.site.register(AudioFile)
