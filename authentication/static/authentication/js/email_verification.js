const otp = document.getElementById("otp");
const verifyBtn = document.getElementById("verifyBtn");
const resendBtn = document.getElementById("resendBtn");
const timerDisplay = document.getElementById("timer");
const resentMsg = document.getElementById("resentMsg");
const errorMsg = document.getElementById("errorMsg");
const form = document.getElementById("verifyForm");
const resendSection = document.getElementById("resendSection");

let countdown = 30;
let countdownInterval;

// Allow only numeric input
otp.addEventListener("input", () => {
  otp.value = otp.value.replace(/[^0-9]/g, '');
  validateForm();
});

// Validate OTP field
function validateForm() {
  if (otp.value.length === 6) {
    verifyBtn.disabled = false;
    verifyBtn.classList.add("enabled");
    errorMsg.textContent = "";
  } else {
    verifyBtn.disabled = true;
    verifyBtn.classList.remove("enabled");
    errorMsg.textContent = "Please enter a valid 6-digit OTP code.";
  }
}



// Start countdown timer
function startTimer() {
  countdown = 30;
  timerDisplay.textContent = `00:${countdown < 10 ? '0' + countdown : countdown}`;
  timerDisplay.style.display = "inline"; // show timer
  resendBtn.disabled = true;
  resendBtn.classList.remove("enabled");
  countdownInterval = setInterval(() => {
    countdown--;
    timerDisplay.textContent = `00:${countdown < 10 ? '0' + countdown : countdown}`;
    if (countdown <= 0) {
      clearInterval(countdownInterval);
      resendBtn.disabled = false;
      resendBtn.classList.add("enabled");
      timerDisplay.style.display = "none"; // hide timer when done
    }
  }, 1000);
}

// Resend OTP
resendBtn.addEventListener("click", () => {
  if (!resendBtn.disabled) {
    startTimer();
    resentMsg.textContent = "A new OTP code has been sent to your email.";
    resentMsg.style.display = "block";
    setTimeout(() => {
      resentMsg.style.display = "none";
    }, 5000);
  }
});

// Initialize on load
window.onload = function() {
  startTimer();
};
