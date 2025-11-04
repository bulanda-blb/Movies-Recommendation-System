

// helper to read the CSRF token cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      c = c.trim();
      if (c.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(c.substring(name.length+1));
        break;
      }
    }
  }
  return cookieValue;
}

document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('historyGrid');
  if (!grid) return;

  grid.addEventListener('click', e => {
    const btn = e.target.closest('.remove-history');
    if (!btn) return;

    const card = btn.closest('.history-card');
    const hid  = card.dataset.id;
    if (!hid) return;

    fetch(window.deleteHistoryUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCookie('csrftoken'),
      },
      body: JSON.stringify({ id: hid })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        card.remove();
      } else {
        alert(data.error || 'Could not delete entry.');
      }
    })
    .catch(() => {
      alert('Network error.');
    });
  });
});
