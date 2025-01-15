from django.contrib import admin
from main.models import Lists, Songs, ListSong

# Register your models here.
admin.site.register(Lists)
admin.site.register(Songs)
admin.site.register(ListSong)