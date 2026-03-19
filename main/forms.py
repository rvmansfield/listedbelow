from django import forms
from .models import MusicList, Song, ListInvite


class MusicListForm(forms.ModelForm):
    class Meta:
        model = MusicList
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'List name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
        }


class ListSettingsForm(forms.ModelForm):
    class Meta:
        model = MusicList
        fields = ['is_public', 'is_coop']
        widgets = {
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_coop': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_public': 'Public — anyone can view this list (no login required)',
            'is_coop': 'Co-op — logged-in users with access can add songs and vote',
        }


class SongManualForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Song title'}),
    )
    artist = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Artist name'}),
    )


class SongSpotifyForm(forms.Form):
    spotify_id = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(widget=forms.HiddenInput())
    artist = forms.CharField(widget=forms.HiddenInput())
    spotify_url = forms.URLField(required=False, widget=forms.HiddenInput())
    album_art_url = forms.URLField(required=False, widget=forms.HiddenInput())


class ListInviteForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address to invite'}),
    )
