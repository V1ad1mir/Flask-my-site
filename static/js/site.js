const icon = document.getElementById('toggle1');
let password = document.getElementById('password1');

/* Event fired when <i> is clicked */
icon.addEventListener('click', function() {
  if(password.type === "password") {
    password.type = "text";
    icon.classList.add("fa-eye-slash");
    icon.classList.remove("fa-eye");
  }
  else {
    password.type = "password";
    icon.classList.add("fa-eye");
    icon.classList.remove("fa-eye-slash");
  }
});

const icon2 = document.getElementById('toggle2');
let password2 = document.getElementById('password2');

icon2.addEventListener('mousedown', function() {
  if(password2.type === "password") {
    password2.type = "text";
    icon2.classList.add("fa-eye-slash");
    icon2.classList.remove("fa-eye");
  }
  else {
    password2.type = "password";
    icon2.classList.add("fa-eye");
    icon2.classList.remove("fa-eye-slash");
  }
});
