from django.contrib import admin
# from . models import TodoItem
# Register your models here.

# admin.site.register(TodoItem)
from django.contrib import admin
from .models import AudioFile

# Register MP3File model to make it visible in the admin
admin.site.register(AudioFile)
