// Elements
const emailModal    = document.getElementById('emailModal');
const pwdModal      = document.getElementById('pwdModal');
const editEmailBtn  = document.getElementById('editEmailBtn');
const changePwdBtn  = document.getElementById('changePwdBtn');
const closeEmailBtn = document.getElementById('closeEmailModal');
const closePwdBtn   = document.getElementById('closePwdModal');

const emailInput    = document.getElementById('newEmail');
const emailError    = document.getElementById('emailError');
const submitEmail   = document.getElementById('submitEmailBtn');

const pwdInput      = document.getElementById('newPassword');
const confirmInput  = document.getElementById('confirmPassword');
const pwdError      = document.getElementById('pwdError');
const submitPwd     = document.getElementById('submitPwdBtn');

// Show modals
editEmailBtn.onclick = () => openModal(emailModal);
changePwdBtn.onclick = () => openModal(pwdModal);
function openModal(modal) {
  modal.style.display = 'flex';
}

// Close modals
closeEmailBtn.onclick = () => emailModal.style.display = 'none';
closePwdBtn.onclick   = () => pwdModal.style.display = 'none';
window.onclick = e => {
  if (e.target === emailModal) emailModal.style.display = 'none';
  if (e.target === pwdModal)   pwdModal.style.display = 'none';
};

// Email validation
emailInput.addEventListener('input', () => {
  const val = emailInput.value.trim();
  const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  if (!valid) {
    emailError.textContent = 'Invalid email format.';
    toggleButton(submitEmail, false);
  } else {
    emailError.textContent = '';
    toggleButton(submitEmail, true);
  }
});

// Password validation
function validPwd(pw) {
  return /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$/.test(pw);
}
[pwdInput, confirmInput].forEach(el => {
  el.addEventListener('input', () => {
    const pw = pwdInput.value;
    const cp = confirmInput.value;
    if (!validPwd(pw)) {
      pwdError.textContent = 'Pwd: uppercase,8–16 chars,digit&special.';
      toggleButton(submitPwd, false);
    } else if (pw !== cp) {
      pwdError.textContent = 'Passwords do not match.';
      toggleButton(submitPwd, false);
    } else {
      pwdError.textContent = '';
      toggleButton(submitPwd, true);
    }
  });
});

// Helper to enable/disable buttons
function toggleButton(btn, enabled) {
  if (enabled) btn.classList.add('enabled'), btn.disabled = false;
  else         btn.classList.remove('enabled'), btn.disabled = true;
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(cookie => {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}

const notifyToggle = document.getElementById('notifyToggle');
const profileInfo  = document.querySelector('.profile-info');
const profileUrl   = profileInfo.getAttribute('data-url');
const csrfToken    = getCookie('csrftoken');

notifyToggle.addEventListener('change', e => {
  const formData = new FormData();
  formData.append('action', 'notify');
  formData.append('notify', e.target.checked);

  fetch(profileUrl, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'X-CSRFToken': csrfToken
    },
    body: formData
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(json => {
        throw new Error(json.error || `Status ${response.status}`);
      });
    }
    return response.json();
  })
  .then(json => {
    console.log('Notification toggled:', json.notify);
  })
  .catch(err => {
    console.error('Error updating notifications:', err);
    // roll back checkbox UI if you like:
    notifyToggle.checked = !notifyToggle.checked;
  });
});