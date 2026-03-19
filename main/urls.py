from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # List CRUD
    path('lists/create/', views.list_create, name='list_create'),
    path('lists/<int:pk>/', views.list_detail, name='list_detail'),
    path('lists/<int:pk>/edit/', views.list_edit, name='list_edit'),
    path('lists/<int:pk>/settings/', views.list_settings, name='list_settings'),
    path('lists/<int:pk>/delete/', views.list_delete, name='list_delete'),

    # Songs
    path('lists/<int:pk>/add-song/', views.song_add, name='song_add'),
    path('lists/<int:pk>/remove-song/<int:ls_pk>/', views.song_remove, name='song_remove'),

    # Voting
    path('lists/<int:pk>/vote/<int:ls_pk>/', views.vote_toggle, name='vote_toggle'),

    # Collaborators & Invites
    path('lists/<int:pk>/invite/<int:inv_pk>/revoke/', views.invite_revoke, name='invite_revoke'),
    path('lists/<int:pk>/collaborators/<int:collab_pk>/remove/', views.collab_remove, name='collab_remove'),

    # Join flows
    path('join/<uuid:token>/', views.join_via_link, name='join_via_link'),
    path('invite/accept/<uuid:token>/', views.invite_accept, name='invite_accept'),

    # Spotify search (AJAX)
    path('spotify/search/', views.spotify_search, name='spotify_search'),
]
