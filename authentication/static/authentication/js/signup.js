

document.addEventListener('DOMContentLoaded', () => {

  const backendError = document.getElementById('backend-error');
  if (backendError) {
    setTimeout(() => {
      backendError.style.opacity = '0';
      backendError.addEventListener('transitionend', () => backendError.remove());
    }, 8000);
  }

  const email            = document.getElementById("email");
  const password         = document.getElementById("password");
  const confirmPassword  = document.getElementById("confirmPassword");
  const termsCheck       = document.getElementById("termsCheck");
  const registerBtn      = document.getElementById("registerBtn");
  const errorMsg         = document.getElementById("errorMsg");

  let touched = { email: false, password: false, confirm: false };

  // 4. VALIDATION FUNCTIONS
  function validatePassword(pw) {
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])[A-Za-z\d\S]{8,16}$/;
    return passwordRegex.test(pw);
  }

  function validateForm() {
    const emailVal   = email.value.trim();
    const passVal    = password.value;
    const confirmVal = confirmPassword.value;
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal);
    const passValid  = validatePassword(passVal);
    const passMatch  = passVal === confirmVal;
    const allFilled  = emailVal && passVal && confirmVal;
    const allChecked = termsCheck.checked;

    const canSubmit = emailValid && passValid && passMatch && allFilled && allChecked;
    registerBtn.disabled = !canSubmit;
    registerBtn.classList.toggle("enabled", canSubmit);

    // only show errors once user has touched all fields
    if (touched.email && touched.password && touched.confirm) {
      if (!allFilled) {
        errorMsg.textContent = "Please fill in all fields.";
      } else if (!emailValid) {
        errorMsg.textContent = "Invalid email format.";
      } else if (!passValid) {
        errorMsg.textContent = "Password must have 8–16 chars, 1 uppercase, 1 digit & 1 special char.";
      } else if (!passMatch) {
        errorMsg.textContent = "Passwords do not match.";
      } else if (!allChecked) {
        errorMsg.textContent = "Please agree to the terms and conditions.";
      } else {
        errorMsg.textContent = "";
      }
    } else {
      errorMsg.textContent = "";
    }
  }

  // 5. EVENT LISTENERS
  email.addEventListener("input", () => { touched.email = true; validateForm(); });
  password.addEventListener("input", () => { touched.password = true; validateForm(); });
  confirmPassword.addEventListener("input", () => { touched.confirm = true; validateForm(); });
  termsCheck.addEventListener("change", validateForm);

  // 6. SEED 'touched' & RUN INITIAL VALIDATION
  if (email.value.trim() !== "")    touched.email    = true;
  if (password.value !== "")        touched.password = true;
  if (confirmPassword.value !== "") touched.confirm  = true;

  validateForm();
});
