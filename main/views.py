import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from . import spotify as spotify_client
from .forms import (
    ListInviteForm,
    ListSettingsForm,
    MusicListForm,
    SongManualForm,
    SongSpotifyForm,
)
from .models import ListCollaborator, ListInvite, ListSong, MusicList, Song, Vote


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_user_role(user, music_list):
    """Return 'owner', 'contributor', or None for the given user/list combo."""
    if not user.is_authenticated:
        return None
    try:
        collab = ListCollaborator.objects.get(music_list=music_list, user=user)
        return collab.role
    except ListCollaborator.DoesNotExist:
        return None


def require_collaborator(user, music_list):
    """Return True if the user is any kind of collaborator on the list."""
    return get_user_role(user, music_list) is not None


def require_owner(user, music_list):
    """Return True if the user is the owner of the list."""
    return get_user_role(user, music_list) == ListCollaborator.ROLE_OWNER


# ── Public Views ─────────────────────────────────────────────────────────────

def index(request):
    recent_lists = MusicList.objects.filter(is_public=True).select_related('created_by').order_by('-created_at')[:6]
    return render(request, 'main/index.html', {'recent_lists': recent_lists})


# ── Auth-required Views ───────────────────────────────────────────────────────

@login_required
def dashboard(request):
    owned = MusicList.objects.filter(created_by=request.user).order_by('-created_at')
    contributing = MusicList.objects.filter(
        collaborators__user=request.user,
        collaborators__role=ListCollaborator.ROLE_CONTRIBUTOR,
    ).order_by('-created_at')
    return render(request, 'main/dashboard.html', {
        'owned_lists': owned,
        'contributing_lists': contributing,
    })


@login_required
def list_create(request):
    if request.method == 'POST':
        form = MusicListForm(request.POST)
        if form.is_valid():
            music_list = form.save(commit=False)
            music_list.created_by = request.user
            music_list.save()
            messages.success(request, 'List created!')
            return redirect('list_detail', pk=music_list.pk)
    else:
        form = MusicListForm()
    return render(request, 'main/list_create.html', {'form': form})


def list_detail(request, pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    role = get_user_role(request.user, music_list)

    # Determine access
    token_str = str(music_list.share_token)
    has_link_access = token_str in request.session.get('rj_list_tokens', [])
    is_viewer = False  # read-only visitor (public or share-link)
    if role is None:
        if music_list.is_public:
            is_viewer = True
        elif has_link_access:
            is_viewer = True
        elif not request.user.is_authenticated:
            return redirect(f'/accounts/login/?next=/lists/{pk}/')
        else:
            return render(request, 'main/list_no_access.html', {'music_list': music_list}, status=403)

    # Annotate list_songs with user vote info
    list_songs = ListSong.objects.filter(music_list=music_list).select_related('song', 'added_by')
    voted_ids = set()
    if request.user.is_authenticated:
        voted_ids = set(
            Vote.objects.filter(user=request.user, list_song__music_list=music_list)
            .values_list('list_song_id', flat=True)
        )
    song_data = []
    for ls in list_songs:
        song_data.append({
            'list_song': ls,
            'vote_count': ls.votes.count(),
            'user_voted': ls.id in voted_ids,
        })
    song_data.sort(key=lambda x: (-x['vote_count'], x['list_song'].added_at))

    has_access = role is not None or (is_viewer and request.user.is_authenticated)
    can_add = role == ListCollaborator.ROLE_OWNER or (music_list.is_coop and has_access)
    can_vote = music_list.is_coop and has_access

    manual_form = SongManualForm()
    spotify_form = SongSpotifyForm()
    spotify_enabled = spotify_client.is_configured()

    share_url = request.build_absolute_uri(f'/join/{music_list.share_token}/')

    return render(request, 'main/list_detail.html', {
        'music_list': music_list,
        'song_data': song_data,
        'role': role,
        'is_viewer': is_viewer,
        'can_add': can_add,
        'can_vote': can_vote,
        'manual_form': manual_form,
        'spotify_form': spotify_form,
        'spotify_enabled': spotify_enabled,
        'share_url': share_url,
    })


@login_required
def list_edit(request, pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    if not require_owner(request.user, music_list):
        return HttpResponseForbidden('Only the list owner can edit this list.')
    if request.method == 'POST':
        form = MusicListForm(request.POST, instance=music_list)
        if form.is_valid():
            form.save()
            messages.success(request, 'List updated.')
            return redirect('list_detail', pk=pk)
    else:
        form = MusicListForm(instance=music_list)
    return render(request, 'main/list_edit.html', {'form': form, 'music_list': music_list})


@login_required
def list_settings(request, pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    if not require_owner(request.user, music_list):
        return HttpResponseForbidden('Only the list owner can manage settings.')

    settings_form = ListSettingsForm(instance=music_list)
    invite_form = ListInviteForm()
    collaborators = ListCollaborator.objects.filter(music_list=music_list).select_related('user')
    pending_invites = ListInvite.objects.filter(music_list=music_list, accepted=False)
    share_url = request.build_absolute_uri(f'/join/{music_list.share_token}/')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'settings':
            settings_form = ListSettingsForm(request.POST, instance=music_list)
            if settings_form.is_valid():
                settings_form.save()
                messages.success(request, 'Settings saved.')
                return redirect('list_settings', pk=pk)

        elif action == 'invite':
            invite_form = ListInviteForm(request.POST)
            if invite_form.is_valid():
                email = invite_form.cleaned_data['email']
                # Don't invite existing collaborators
                already_collab = ListCollaborator.objects.filter(
                    music_list=music_list, user__email=email
                ).exists()
                if already_collab:
                    messages.warning(request, f'{email} is already a collaborator.')
                else:
                    invite, created = ListInvite.objects.get_or_create(
                        music_list=music_list,
                        email=email,
                        defaults={'invited_by': request.user},
                    )
                    if created:
                        _send_invite_email(request, invite)
                        messages.success(request, f'Invitation sent to {email}.')
                    else:
                        messages.warning(request, f'An invite already exists for {email}.')
                return redirect('list_settings', pk=pk)

    return render(request, 'main/list_settings.html', {
        'music_list': music_list,
        'settings_form': settings_form,
        'invite_form': invite_form,
        'collaborators': collaborators,
        'pending_invites': pending_invites,
        'share_url': share_url,
    })


def _send_invite_email(request, invite):
    accept_url = request.build_absolute_uri(f'/invite/accept/{invite.token}/')
    subject = render_to_string(
        'main/email/list_invite_subject.txt',
        {'invite': invite},
    ).strip()
    body = render_to_string(
        'main/email/list_invite_message.txt',
        {'invite': invite, 'accept_url': accept_url},
    )
    send_mail(subject, body, None, [invite.email], fail_silently=True)


@login_required
@require_POST
def list_delete(request, pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    if not require_owner(request.user, music_list):
        return HttpResponseForbidden('Only the list owner can delete this list.')
    music_list.delete()
    messages.success(request, 'List deleted.')
    return redirect('dashboard')


# ── Song Views ────────────────────────────────────────────────────────────────

@login_required
@require_POST
def song_add(request, pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    role = get_user_role(request.user, music_list)
    token_str = str(music_list.share_token)
    has_link_access = token_str in request.session.get('rj_list_tokens', [])
    has_access = role is not None or music_list.is_public or has_link_access
    can_add = role == ListCollaborator.ROLE_OWNER or (music_list.is_coop and has_access)
    if not can_add:
        return HttpResponseForbidden('Adding songs is not enabled for this list.')

    source = request.POST.get('source', 'manual')

    if source == 'spotify':
        form = SongSpotifyForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            song, _ = Song.objects.get_or_create(
                spotify_id=d['spotify_id'],
                defaults={
                    'title': d['title'],
                    'artist': d['artist'],
                    'spotify_url': d.get('spotify_url', ''),
                    'album_art_url': d.get('album_art_url', ''),
                    'added_by': request.user,
                },
            )
            try:
                ListSong.objects.create(music_list=music_list, song=song, added_by=request.user)
                messages.success(request, f'"{song.title}" added to the list.')
            except IntegrityError:
                messages.warning(request, 'That song is already on this list.')
        else:
            messages.error(request, 'Invalid song data.')
    else:
        form = SongManualForm(request.POST)
        if form.is_valid():
            song = Song.objects.create(
                title=form.cleaned_data['title'],
                artist=form.cleaned_data['artist'],
                added_by=request.user,
            )
            try:
                ListSong.objects.create(music_list=music_list, song=song, added_by=request.user)
                messages.success(request, f'"{song.title}" added to the list.')
            except IntegrityError:
                messages.warning(request, 'That song is already on this list.')
        else:
            messages.error(request, 'Please provide both a title and artist.')

    return redirect('list_detail', pk=pk)


@login_required
@require_POST
def song_remove(request, pk, ls_pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    list_song = get_object_or_404(ListSong, pk=ls_pk, music_list=music_list)
    role = get_user_role(request.user, music_list)
    if role != ListCollaborator.ROLE_OWNER:
        return HttpResponseForbidden('Only the list owner can remove songs.')
    list_song.delete()
    messages.success(request, 'Song removed.')
    return redirect('list_detail', pk=pk)


# ── Vote View ─────────────────────────────────────────────────────────────────

@login_required
@require_POST
def vote_toggle(request, pk, ls_pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    list_song = get_object_or_404(ListSong, pk=ls_pk, music_list=music_list)

    token_str = str(music_list.share_token)
    has_link_access = token_str in request.session.get('rj_list_tokens', [])
    has_access = require_collaborator(request.user, music_list) or music_list.is_public or has_link_access
    if not has_access:
        return HttpResponseForbidden()
    if not music_list.is_coop:
        return HttpResponseForbidden('Co-op is not enabled for this list.')

    vote, created = Vote.objects.get_or_create(user=request.user, list_song=list_song)
    if not created:
        vote.delete()
        voted = False
    else:
        voted = True

    vote_count = list_song.votes.count()

    # AJAX response for JS-driven toggle
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'voted': voted, 'vote_count': vote_count})

    return redirect('list_detail', pk=pk)


# ── Invite & Join Views ───────────────────────────────────────────────────────

@login_required
@require_POST
def invite_revoke(request, pk, inv_pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    if not require_owner(request.user, music_list):
        return HttpResponseForbidden()
    invite = get_object_or_404(ListInvite, pk=inv_pk, music_list=music_list)
    invite.delete()
    messages.success(request, 'Invite revoked.')
    return redirect('list_settings', pk=pk)


@login_required
@require_POST
def collab_remove(request, pk, collab_pk):
    music_list = get_object_or_404(MusicList, pk=pk)
    if not require_owner(request.user, music_list):
        return HttpResponseForbidden()
    collab = get_object_or_404(ListCollaborator, pk=collab_pk, music_list=music_list)
    if collab.role == ListCollaborator.ROLE_OWNER:
        return HttpResponseForbidden('Cannot remove the owner.')
    collab.delete()
    messages.success(request, 'Collaborator removed.')
    return redirect('list_settings', pk=pk)


@login_required
def join_via_link(request, token):
    music_list = get_object_or_404(MusicList, share_token=token)
    token_str = str(music_list.share_token)
    tokens = request.session.get('rj_list_tokens', [])
    if token_str not in tokens:
        tokens.append(token_str)
        request.session['rj_list_tokens'] = tokens
    return redirect('list_detail', pk=music_list.pk)


@login_required
def invite_accept(request, token):
    invite = get_object_or_404(ListInvite, token=token)

    if invite.accepted:
        messages.info(request, 'This invite has already been accepted.')
        return redirect('list_detail', pk=invite.music_list.pk)

    if request.method == 'POST':
        invite.accepted = True
        invite.accepted_at = timezone.now()
        invite.save()
        ListCollaborator.objects.get_or_create(
            music_list=invite.music_list,
            user=request.user,
            defaults={
                'role': ListCollaborator.ROLE_CONTRIBUTOR,
                'added_by': invite.invited_by,
            },
        )
        messages.success(request, f'You\'ve joined "{invite.music_list.title}"!')
        return redirect('list_detail', pk=invite.music_list.pk)

    return render(request, 'main/invite_accept.html', {'invite': invite})


# ── Spotify Search View ───────────────────────────────────────────────────────

@login_required
def spotify_search(request):
    if not spotify_client.is_configured():
        return JsonResponse({'error': 'Spotify not configured'}, status=503)
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    results = spotify_client.search_tracks(query)
    return JsonResponse({'results': results})
