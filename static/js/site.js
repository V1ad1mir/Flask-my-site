/**
* This function toggles the visibility of two password input fields when a user clicks on corresponding icons.
* It first selects the icons and password fields using their IDs and adds event listeners to them.
* When a user clicks on the icon, the function checks if the corresponding password field is currently hidden (type="password").
* If it is hidden, it changes the type to "text" to reveal the password and updates the icon to show a crossed-out eye.
* If it is already visible (type="text"), it changes the type back to "password" to hide the password and updates the icon to show a normal eye.
**/

function togglePasswordVisibility(icon, passwordField) {
  if(passwordField.type === "password") {
    passwordField.type = "text";
    icon.classList.add("fa-eye-slash");
    icon.classList.remove("fa-eye");
  }
  else {
    passwordField.type = "password";
    icon.classList.add("fa-eye");
    icon.classList.remove("fa-eye-slash");
  }
}

const icon1 = document.getElementById('toggle1');
const password1 = document.getElementById('password2');
icon1.addEventListener('mousedown', function() {
  togglePasswordVisibility(icon1, password1);
});

const icon2 = document.getElementById('toggle2');
const password2 = document.getElementById('password1');
icon2.addEventListener('mousedown', function() {
  togglePasswordVisibility(icon2, password2);
});

/**
 * Toggles the 'show' class on the element with id 'collapse'.
 */

function toggle () {
  document.getElementById("collapse").classList.toggle("show");
}


// Function to toggle between light and dark themes

function toggleTheme() {
  var root = document.documentElement;
  var theme = getCookie('theme');
  if (theme === 'dark') {
    root.classList.remove('dark-theme');
    setCookie('theme', 'light', 365);
  } else {
    root.classList.add('dark-theme');
    setCookie('theme', 'dark', 365);
  }
}

// Check if a theme preference has already been set
var theme = getCookie('theme');
if (theme === 'dark') {
  var root = document.documentElement;
  root.classList.add('dark-theme');
}

// Function to get a cookie by name
function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
}

// Function to set a cookie
function setCookie(name, value, days) {
  var expires = "";
  if (days) {
    var date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    expires = "; expires=" + date.toUTCString();
  }
  document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

/**
 * Toggles the size of a given photo by adding or removing the 'bigger' class.
 * @param {HTMLElement} photo - The photo element to toggle the size of.
 */
function togglePhotoSize(photo) {
  photo.classList.toggle('bigger');
}


/**
 * Replaces the span elements containing travel data with input elements for editing
 * @param {number} d - The ID of the travel data row to be edited
 */

function edit(d) {
  // Get the span elements and replace them with input elements
  ['country', 'monthyear', 'cities', 'duration', 'budget', 'rating'].forEach(function(property) {
    var span = document.getElementById(property + '_' + d);
    span.innerHTML = '<input type="' + (property === 'duration' ? 'number" min="1"' : 'text') + ' name="' + property + '" value="' + span.innerHTML + '">';
  });

  // Change the button text to "Save" and attach the save function
  var edit_button = document.getElementById('edit_button_' + d);
  edit_button.innerHTML = 'Save';
  edit_button.onclick = function() {
    save(d);
  };
}

function showInput(event) {
  event.preventDefault();
  var input = document.getElementById("search_field");
  if (input.style.visibility === "hidden") {
    input.style.visibility = "visible";
    input.style.width = "150px";
  }
}

