

function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

document.addEventListener('DOMContentLoaded', () => {
  const grid     = document.getElementById('watchlistGrid');
  const sortSel  = document.getElementById('sortSelect');
  const filtSel  = document.getElementById('filterSelect');

  // 1) Remove from watchlist via AJAX, then drop the card
  grid.addEventListener('click', e => {
    const btn = e.target.closest('.remove-btn');
    if (!btn) return;
    const card    = btn.closest('.movie-card');
    const movieId = card.dataset.movieId;
    const url     = btn.dataset.url;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({ movie_id: movieId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        card.remove();
      } else if (data.redirect) {
        window.location = data.redirect;
      } else {
        alert(data.error || 'Could not remove');
      }
    })
    .catch(() => alert('Network error.'));
  });

  // 2) Sorting: reload with new ?sort=
  sortSel.addEventListener('change', e => {
    const params = new URLSearchParams(window.location.search);
    params.set('sort', e.target.value);
    params.delete('page');
    window.location.search = params.toString();
  });

  // 3) Filtering: reload with new ?genre=
  filtSel.addEventListener('change', e => {
    const params = new URLSearchParams(window.location.search);
    params.set('genre', e.target.value);
    params.delete('page');
    window.location.search = params.toString();
  });
});
