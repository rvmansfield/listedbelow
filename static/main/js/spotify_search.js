/**
 * Spotify track search for ListedBelow.
 * Fetches results from /spotify/search/?q=... and renders them as selectable cards.
 * Selecting a card submits a hidden form to add the song to the current list.
 */
(function () {
  'use strict';

  const searchBtn = document.getElementById('spotifySearchBtn');
  const queryInput = document.getElementById('spotifyQuery');
  const resultsContainer = document.getElementById('spotifyResults');

  if (!searchBtn || !queryInput || !resultsContainer) return;

  // Detect current list pk from the add-song form action URL
  const addSongForm = document.querySelector('form[action*="add-song"]');
  const addSongUrl = addSongForm ? addSongForm.action : null;
  const csrfToken = addSongForm
    ? addSongForm.querySelector('[name=csrfmiddlewaretoken]').value
    : '';

  async function doSearch() {
    const query = queryInput.value.trim();
    if (!query) return;

    searchBtn.disabled = true;
    searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
    resultsContainer.innerHTML = '';

    try {
      const res = await fetch(`/spotify/search/?q=${encodeURIComponent(query)}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await res.json();
      renderResults(data.results || []);
    } catch (err) {
      resultsContainer.innerHTML =
        '<div class="text-danger small">Search failed. Please try again.</div>';
    } finally {
      searchBtn.disabled = false;
      searchBtn.innerHTML = '<i class="bi bi-search"></i> Search';
    }
  }

  function renderResults(tracks) {
    if (!tracks.length) {
      resultsContainer.innerHTML = '<p class="text-muted small">No results found.</p>';
      return;
    }

    const list = document.createElement('div');
    list.className = 'list-group';

    tracks.forEach((track) => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className =
        'list-group-item list-group-item-action bg-transparent border-secondary spotify-result-card d-flex align-items-center gap-3 p-2';

      item.innerHTML = `
        ${track.album_art_url
          ? `<img src="${escHtml(track.album_art_url)}" alt="Album art" style="width:40px;height:40px;object-fit:cover;" class="rounded">`
          : `<div style="width:40px;height:40px;" class="rounded bg-secondary d-flex align-items-center justify-content-center"><i class="bi bi-music-note text-muted"></i></div>`
        }
        <div class="text-start min-width-0">
          <div class="fw-semibold text-truncate">${escHtml(track.title)}</div>
          <div class="text-muted small text-truncate">${escHtml(track.artist)}</div>
        </div>
        <i class="bi bi-plus-circle ms-auto text-primary"></i>
      `;

      item.addEventListener('click', () => addSpotifyTrack(track));
      list.appendChild(item);
    });

    resultsContainer.appendChild(list);
  }

  function addSpotifyTrack(track) {
    if (!addSongUrl) return;
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = addSongUrl;
    form.style.display = 'none';

    const fields = {
      csrfmiddlewaretoken: csrfToken,
      source: 'spotify',
      spotify_id: track.id,
      title: track.title,
      artist: track.artist,
      spotify_url: track.spotify_url || '',
      album_art_url: track.album_art_url || '',
    };

    Object.entries(fields).forEach(([name, value]) => {
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = name;
      input.value = value;
      form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
  }

  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  searchBtn.addEventListener('click', doSearch);
  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      doSearch();
    }
  });
})();
