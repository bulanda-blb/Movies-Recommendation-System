document.addEventListener('DOMContentLoaded', () => {
  const btn     = document.getElementById('watchlistBtn');
  const movieId = btn.dataset.movieId;

  // 1) Toggle watchlist via AJAX
  btn.addEventListener('click', () => {
    fetch(TOGGLE_WATCHLIST_URL, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ movie_id: movieId })
    })
    .then(r => r.json())
    .then(data => {
      if (data.status === 'ok') {
        btn.textContent = data.action === 'added'
          ? 'Remove from Watchlist'
          : 'Save to Watchlist';
        // also toggle button color:
        btn.classList.toggle('gold', data.action === 'added');
        btn.classList.toggle('white', data.action === 'removed');
      } else if (data.redirect) {
        window.location = data.redirect;
      }
    })
    .catch(console.error);
  });

  // 2) Fetch and embed trailer
  fetch(`https://api.themoviedb.org/3/movie/${movieId}/videos?api_key=${TMDB_API_KEY}`)
    .then(r => r.json())
    .then(data => {
      const c = document.getElementById('trailerContainer');
      const vids = data.results.filter(v=>v.site==='YouTube'&&v.type==='Trailer');
      if (vids.length) {
        c.innerHTML = `
          <iframe
            src="https://www.youtube.com/embed/${vids[0].key}"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
          </iframe>`;
      } else {
        c.textContent = 'No trailer found.';
      }
    })
    .catch(() => {
      document.getElementById('trailerContainer')
              .textContent = 'Trailer could not be loaded.';
    });
});
