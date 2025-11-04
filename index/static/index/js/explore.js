document.addEventListener('DOMContentLoaded', () => {
  // Smooth scroll on pagination click
  document.querySelectorAll('.pagination a').forEach(link => {
    link.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // Filter button behavior
  document.querySelectorAll('.filter-buttons button').forEach(btn => {
    btn.addEventListener('click', () => {
      const f = btn.dataset.filter;
      const params = new URLSearchParams(window.location.search);
      params.set('filter', f);
      params.delete('page');
      window.location.search = params.toString();
    });
  });
});
