// static/index/js/watchlist.js

function getCookie(name) {
  const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return v ? v.pop() : '';
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.watchlist-btn').forEach(btn => {
    console.log('Found watchlist button');
    btn.addEventListener('click', function () {
      const card     = this.closest('.movie-card');
      const movieId  = card.dataset.movieId;
      const toggleUrl = this.dataset.url;
      console.log('Toggling watchlist for movie', movieId, 'via', toggleUrl);

      fetch(toggleUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ movie_id: movieId })
      })
      .then(response => {
        console.log('Raw response:', response);
        return response.json();
      })
      .then(data => {
        console.log('JSON data:', data);
        if (data.redirect) {
          window.location = data.redirect;
        } else if (data.status === 'ok') {
          this.classList.toggle('saved', data.action === 'added');
        } else if (data.error) {
          alert(data.error);
        }
      })
      .catch(err => console.error('Fetch error:', err));
    });
  });
});
