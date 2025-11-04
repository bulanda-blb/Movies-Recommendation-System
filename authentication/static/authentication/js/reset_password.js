const email = document.getElementById("email");
const newPassword = document.getElementById("newPassword");
const confirmPassword = document.getElementById("confirmPassword");
const resetBtn = document.getElementById("resetBtn");
const errorMsg = document.getElementById("errorMsg");
const form = document.getElementById("resetForm");

// Flags to know if user has interacted
let touched = {
  email: false,
  password: false,
  confirm: false
};

// Email validation function
function validateEmail(emailValue) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(emailValue);
}

// Password validation function
function validatePassword(pw) {
  const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])[A-Za-z\d\S]{8,16}$/;
  return passwordRegex.test(pw);
}

// Form validation
function validateForm() {
  const emailVal = email.value.trim();
  const passVal = newPassword.value;
  const confirmVal = confirmPassword.value;

  const emailValid = validateEmail(emailVal);
  const passValid = validatePassword(passVal);
  const passMatch = passVal === confirmVal;
  const allFilled = emailVal && passVal && confirmVal;

  let canSubmit = emailValid && passValid && passMatch && allFilled;
  resetBtn.disabled = !canSubmit;
  resetBtn.classList.toggle("enabled", canSubmit);

  // Show errors only after user has interacted with all fields
  if (touched.email && touched.password && touched.confirm) {
    if (!allFilled) {
      errorMsg.textContent = "Please fill in all fields.";
    } else if (!emailValid) {
      errorMsg.textContent = "Invalid email format.";
    } else if (!passValid) {
      errorMsg.textContent = "Password must start with uppercase, 8-16 chars, include digit and special char.";
    } else if (!passMatch) {
      errorMsg.textContent = "Passwords do not match.";
    } else {
      errorMsg.textContent = "";
    }
  } else {
    errorMsg.textContent = "";
  }
}

// Event Listeners with Interaction Tracking
email.addEventListener("input", () => {
  touched.email = true;
  validateForm();
});

newPassword.addEventListener("input", () => {
  touched.password = true;
  validateForm();
});

confirmPassword.addEventListener("input", () => {
  touched.confirm = true;
  validateForm();
});


