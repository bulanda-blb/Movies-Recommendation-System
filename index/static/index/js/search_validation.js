// index/static/index/js/search_validation.js

document.addEventListener('DOMContentLoaded', () => {
  const formInput  = document.querySelector('.search-form .search-input');
  const submitBtn  = document.querySelector('.search-form .search-btn');

  if (!formInput || !submitBtn) return;

  // Enable/disable button based on whether there’s any non-whitespace
  function updateButtonState() {
    const hasText = formInput.value.trim().length > 0;
    submitBtn.disabled = !hasText;
  }

  // Run on every keystroke
  formInput.addEventListener('input', updateButtonState);

  // Also initialize on page load (handles back/forward)
  updateButtonState();
});
