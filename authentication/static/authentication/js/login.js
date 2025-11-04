

document.addEventListener("DOMContentLoaded", () => {
  // ─── Fade-out signup success ───
  const successEl = document.getElementById("login-success");
  if (successEl) {
    setTimeout(() => {
      successEl.style.opacity = "0";
      successEl.addEventListener("transitionend", () => successEl.remove());
    }, 5000);
  }

  // ─── Real-time validation & error display ───
  const email       = document.getElementById("email");
  const password    = document.getElementById("password");
  const loginBtn    = document.getElementById("loginBtn");
  const errorMsgEl  = document.getElementById("errorMsg");
  let touched = { email: false, password: false };

  function isValidEmail(val) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  }
  function isValidPassword(val) {
    return /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,16}$/.test(val);
  }

  function validateForm() {
    const e       = email.value.trim();
    const p       = password.value;
    const emailOk = isValidEmail(e);
    const passOk  = isValidPassword(p);
    const filled  = e !== "" && p !== "";
    const canDo   = emailOk && passOk && filled;

    loginBtn.disabled = !canDo;
    loginBtn.classList.toggle("enabled", canDo);

    // only show field-level errors once both fields touched
    if (touched.email && touched.password) {
      if (!filled) {
        errorMsgEl.textContent = "Please fill in all fields.";
      } else if (!emailOk) {
        errorMsgEl.textContent = "Invalid email format.";
      } else if (!passOk) {
        errorMsgEl.textContent =
          "Password must be 8–16 chars, start with uppercase, include digit & special char.";
      } else {
        errorMsgEl.textContent = "";
      }
    }
  }

  // wire up “touched” tracking
  email.addEventListener("input", () => {
    touched.email = true;
    validateForm();
  });
  password.addEventListener("input", () => {
    touched.password = true;
    validateForm();
  });

  // if the page was re-rendered with a backend error, we still want validation on load
  if (email.value.trim() !== "")    touched.email    = true;
  if (password.value !== "")        touched.password = true;
  validateForm();
});
