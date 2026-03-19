import uuid
from django.db import models
from django.contrib.auth.models import User


class MusicList(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='owned_lists'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    share_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_public = models.BooleanField(
        default=False,
        help_text='When enabled, any visitor can view this list without logging in.',
    )
    is_coop = models.BooleanField(
        default=False,
        help_text='When enabled, any logged-in user with access can add songs and vote.',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    spotify_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    spotify_url = models.URLField(blank=True, null=True)
    album_art_url = models.URLField(blank=True, null=True)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='songs_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['artist', 'title']

    def __str__(self):
        return f'{self.title} — {self.artist}'


class ListSong(models.Model):
    music_list = models.ForeignKey(
        MusicList, on_delete=models.CASCADE, related_name='list_songs'
    )
    song = models.ForeignKey(
        Song, on_delete=models.CASCADE, related_name='list_songs'
    )
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='list_songs_added'
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('music_list', 'song')
        ordering = ['added_at']

    def __str__(self):
        return f'{self.song} on {self.music_list}'

    @property
    def vote_count(self):
        return self.votes.count()


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    list_song = models.ForeignKey(
        ListSong, on_delete=models.CASCADE, related_name='votes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'list_song')

    def __str__(self):
        return f'{self.user.username} voted for {self.list_song}'


class ListCollaborator(models.Model):
    ROLE_OWNER = 'owner'
    ROLE_CONTRIBUTOR = 'contributor'
    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_CONTRIBUTOR, 'Contributor'),
    ]

    music_list = models.ForeignKey(
        MusicList, on_delete=models.CASCADE, related_name='collaborators'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='collaborations'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CONTRIBUTOR)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collaborators_added',
    )

    class Meta:
        unique_together = ('music_list', 'user')

    def __str__(self):
        return f'{self.user.username} ({self.role}) on {self.music_list}'

    @property
    def is_owner(self):
        return self.role == self.ROLE_OWNER


class ListInvite(models.Model):
    music_list = models.ForeignKey(
        MusicList, on_delete=models.CASCADE, related_name='invites'
    )
    email = models.EmailField()
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='invites_sent'
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('music_list', 'email')

    def __str__(self):
        status = 'accepted' if self.accepted else 'pending'
        return f'Invite for {self.email} to {self.music_list} ({status})'
