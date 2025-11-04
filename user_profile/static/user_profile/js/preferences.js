const form = document.getElementById('preferencesForm');
const saveBtn = document.getElementById('savePrefBtn');

const requirements = [
  { name: 'genre',     type: 'checkbox', min: 1 },
  { name: 'mood',      type: 'checkbox', min: 1 },
  { name: 'length',    type: 'radio',    min: 1 },
  { name: 'context',   type: 'radio',    min: 1 },
  { name: 'frequency', type: 'select',   min: 1 },
  { name: 'subtitles', type: 'radio',    min: 1 },
  { name: 'era',       type: 'checkbox', min: 1 },
  { name: 'type',      type: 'checkbox', min: 1 },
];

function updateSaveState() {
  let valid = true;
  requirements.forEach(req => {
    let count = 0;
    if (req.type === 'checkbox' || req.type === 'radio') {
      count = form.querySelectorAll(`input[name="${req.name}"]:checked`).length;
    } else {
      const sel = form.querySelector(`select[name="${req.name}"]`);
      count = sel && sel.value ? 1 : 0;
    }
    if (count < req.min) valid = false;
  });
  saveBtn.disabled = !valid;
  saveBtn.classList.toggle('enabled', valid);
}

// run on load
document.addEventListener('DOMContentLoaded', () => {
  updateSaveState();
  form.addEventListener('change', updateSaveState);
});
