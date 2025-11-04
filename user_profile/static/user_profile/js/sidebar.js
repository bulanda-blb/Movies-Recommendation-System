const body = document.body;
const toggleBtn = document.getElementById('sidebarToggle');
const closeBtn  = document.getElementById('sidebarClose');
const links     = document.querySelectorAll('.sidebar-nav a');
const currentPage = body.dataset.page;

// Open sidebar
toggleBtn.addEventListener('click', () => {
  body.classList.replace('sidebar-collapsed', 'sidebar-expanded');
});


closeBtn.addEventListener('click', () => {
  body.classList.replace('sidebar-expanded', 'sidebar-collapsed');
});

// Highlight active link on load and on click
links.forEach(link => {
  // On load
  if (link.dataset.page === currentPage) {
    link.classList.add('active');
  }

  link.addEventListener('click', e => {
    links.forEach(l => l.classList.remove('active'));
    link.classList.add('active');
    
  });
});
