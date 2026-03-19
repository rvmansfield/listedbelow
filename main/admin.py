from django.contrib import admin
from .models import MusicList, Song, ListSong, Vote, ListCollaborator, ListInvite


@admin.register(MusicList)
class MusicListAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_public', 'is_coop')
    list_filter = ('is_public', 'is_coop')
    search_fields = ('title', 'created_by__username')
    readonly_fields = ('share_token', 'created_at', 'updated_at')


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'spotify_id', 'added_by', 'created_at')
    search_fields = ('title', 'artist', 'spotify_id')
    list_filter = ('created_at',)


@admin.register(ListSong)
class ListSongAdmin(admin.ModelAdmin):
    list_display = ('song', 'music_list', 'added_by', 'added_at', 'vote_count')
    list_filter = ('music_list',)
    search_fields = ('song__title', 'song__artist', 'music_list__title')

    def vote_count(self, obj):
        return obj.votes.count()
    vote_count.short_description = 'Votes'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'list_song', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)


@admin.register(ListCollaborator)
class ListCollaboratorAdmin(admin.ModelAdmin):
    list_display = ('user', 'music_list', 'role', 'added_at', 'added_by')
    list_filter = ('role',)
    search_fields = ('user__username', 'music_list__title')


@admin.register(ListInvite)
class ListInviteAdmin(admin.ModelAdmin):
    list_display = ('email', 'music_list', 'invited_by', 'accepted', 'created_at')
    list_filter = ('accepted',)
    search_fields = ('email', 'music_list__title')
    readonly_fields = ('token', 'created_at', 'accepted_at')
