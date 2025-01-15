from django.urls import path
from django.conf.urls import include
from . import views
from .views import vote

urlpatterns = [
    path('', views.index, name='index'),
    path('lists', views.lists, name='lists'),
    path('lists/<int:list_id>', views.list, name='list'),
    path('spotifylists', views.spotifyplaylists, name='spotifylists'),
    path('vote/<int:list_id>/<int:song_id>',views.vote, name='vote'),
    path('importspotify/<str:playlist_id>', views.importspotify, name='importspotify'),
    #path('qr_code/', include('qr_code.urls', namespace="qr_code")),
    
]