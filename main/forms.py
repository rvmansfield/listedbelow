from .models import Lists, Songs
from django.forms import ModelForm
from django import forms

class songForm(ModelForm):

    song_title = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    song_artist = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))


    class Meta:
        model = Songs
        fields = ['song_title', 'song_artist']
        


class listForm(forms.ModelForm):
    
    title = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    allowAdds = forms.BooleanField(required=False, label='Allow Others to Add', widget=forms.CheckboxInput())
    allowVotes = forms.BooleanField(required=False, label='Allow Song Voting', widget=forms.CheckboxInput())

    class Meta:
        model = Lists
        fields = ['title', 'description','allowAdds','allowVotes']