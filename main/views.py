from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.template import loader
from .models import Lists, Songs, ListSong, Vote
from .forms import songForm, listForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views import View
from datetime import date
from django.db.models import Count
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = '020796ff83e847fbb52f782861480f39'
CLIENT_SECRET = 'ba6a918c02034be4884c99a8651058df'
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'playlist-read-private'

# Create your views here.

def index(request):
    topLists = Lists.objects.order_by('-dateCreated').values()
    return render(request, 'index.html',{'topLists': topLists})

@login_required(login_url='login')
def lists(request):
    allLists = Lists.objects.filter(createdBy=request.user.username).order_by('-dateCreated').values()
    page_num = request.GET.get('page', 1)
    paginator = Paginator(allLists, 10) #pagination rows

    if request.method == 'POST':
        listform = listForm(request.POST)
        if listform.is_valid():
            formdata = listform.save(commit=False)
            formdata.dateCreated = date.today()
            formdata.createdBy = request.user.username
            formdata.save()
            listform = listForm()
            
    else:
        listform = listForm()
        print('show form')


    return render(request, 'lists.html', {'allLists': allLists,'listform':listform,})


@login_required(login_url='login')
def spotifyplaylists(request):


    # Authenticate with Spotify
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

    print(sp.current_user())

    user_profile = sp.current_user()
    profile_name = user_profile.get('display_name', 'N/A')

    try:
        playlists = sp.current_user_playlists()
        print("Playlists:")
        for playlist in playlists['items']:
            print(f" - {playlist['name']} - {playlist['description']} (Tracks: {playlist['tracks']['total']})")
    except Exception as e:
        print(f"Error fetching playlists: {e}")


   

    return render(request, 'spotifylists.html', {'playlists': playlists['items']})

def importspotify(request,playlist_id):
    playlist_id = playlist_id

    # Authenticate with Spotify
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))

    try:

        playlist = sp.playlist(playlist_id)
        print(f"Playlist Name: {playlist['name']}")
        print(f"Description: {playlist['description']}")
        print(f"Owner: {playlist['owner']['display_name']}")

        listobj, created = Lists.objects.update_or_create(
            title=playlist['name'],
            description=playlist['description'],
            dateCreated = date.today(),
            createdBy = request.user.username
            
        )

        list_id = listobj.id

        print(f"The new List is {list_id}")



        tracks = sp.playlist_tracks(playlist_id)
        for item in (tracks['items']):
            track = item['track']

            artists = ', '.join(artist['name'] for artist in track['artists']) 

            songobj, created = Songs.objects.update_or_create(
            song_title=track['name'],
            song_artist = artists
            #song_artist=track['artists']
            
            )

            track_id = songobj.id
            print(track_id)
            ListSong.objects.create(list_id=listobj.id, song_id=songobj.id)

            
            #print(f"{track['name']} by {', '.join(artist['name'] for artist in track['artists'])}")
    except Exception as e:
        print(f"Error fetching tracks: {e}")

    return render(request, 'index.html')


def list(request,list_id):
    listsongs = Songs.objects.filter(songlists=list_id).order_by('-id')
    listinfo = Lists.objects.get(id=list_id)
    #qr_url = "http://10.0.0.19:8000/lists/" + str(listinfo.id)
    #votes = Vote.objects.filter(list_id=list_id)
    votes = Vote.objects.values('list', 'song').annotate(count=Count('id'))
    if listinfo.createdBy == request.user.username:
        listowner = 1
    else:
        listowner = 0

    #print(votes)
    
    #print(list_id)
    if request.method == 'POST':
        songform = songForm(request.POST)
        if songform.is_valid():
            new_song = songform.save(commit=False)
            #formdata.songlists = list_id
            new_song.save()
            #print(new_song.id)
            ListSong.objects.create(list_id=list_id, song_id=new_song.id)
            songform = songForm()
            
    else:
        songform = songForm()
        
    return render(request, 'list.html', {'listsongs': listsongs,'songform':songform,'listinfo':listinfo,'votes':votes, 'listowner':listowner})


def vote(request,list_id,song_id):

    votescookie = request.COOKIES.get('votes')

    if votescookie is None:
        votesmade = 0
    else:
        votesmade = int(votescookie)

    if request.user.is_authenticated:
        currentuser = request.user.id
        votecount = 100
    else:
        currentuser = 2
        votecount = 4
    
    if votesmade < votecount:
        Vote.objects.create(list_id=list_id, song_id=song_id, user_id=currentuser)
        response = redirect('/lists/' + str(list_id))
        response.set_cookie('votes', votesmade + 1)
        return response
    else:
        print('Max votes reached')
        return redirect('/lists/' + str(list_id))
        

   
    
    