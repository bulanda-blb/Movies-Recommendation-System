const trendingMovies = [
  {
    title: "Inception",
    genre: "Action | Sci-Fi",
    image: "https://m.media-amazon.com/images/I/71niXI3lxlL._AC_SY679_.jpg"
  },
  {
    title: "Tanhaji",
    genre: "Bollywood | Historical",
    image: "https://upload.wikimedia.org/wikipedia/en/9/9f/Tanhaji_film_poster.jpg"
  },
  {
    title: "Dark Knight",
    genre: "Hollywood | Action",
    image: "https://m.media-amazon.com/images/M/MV5BM2MyNjYxNmYtYTAwMC00ZjQ2LWJhZTEtODkzNDZkYjc2MWQ0XkEyXkFqcGdeQXVyNjUwNzk3NDc@._V1_.jpg"
  },
  {
    title: "Kabaddi",
    genre: "Nepali | Drama",
    image: "https://static.filmAffinity.com/images/movies/170/313/174721_949.jpg"
  }
];

function renderCards(containerId, movies) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  movies.forEach(movie => {
    const card = document.createElement('div');
    card.classList.add('movie-card');
    card.innerHTML = `
      <img src="${movie.image}" alt="${movie.title}" />
      <div class="info">
        <h3>${movie.title}</h3>
        <span>${movie.genre}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

renderCards('trending', trendingMovies);
renderCards('top-rated', trendingMovies);
renderCards('new-releases', trendingMovies);

