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

function toggleForm() {
  var form = document.getElementById("travel-form");
  if (form.style.display === "none") {
    form.style.display = "table"; // Show the form as a table
  } else {
    form.style.display = "none"; // Hide the form
  }
}

function edit(d) {
  // Get the span elements
  var country_span = document.getElementById('country_' + d);
  var monthyear_span = document.getElementById('monthyear_' + d);
  var cities_span = document.getElementById('cities_' + d);
  var duration_span = document.getElementById('duration_' + d);
  var budget_span = document.getElementById('budget_' + d);
  var rating_span = document.getElementById('rating_' + d);

  // Replace the span elements with input elements
  country_span.innerHTML = '<input type="text" name="country" value="' + country_span.innerHTML + '">';
  monthyear_span.innerHTML = '<input type="text" name="monthyear" value="' + monthyear_span.innerHTML + '">';
  cities_span.innerHTML = '<input type="text" name="cities" value="' + cities_span.innerHTML + '">';
  duration_span.innerHTML = '<input type="number" min="1" name="duration" value="' + duration_span.innerHTML + '">';
  budget_span.innerHTML = '<input type="number" step="100" min="100" name="budget" value="' + budget_span.innerHTML + '">';
  rating_span.innerHTML = '<input type="number" name="rating" min="1" max="5" value="' + rating_span.innerHTML + '">';

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



// Add click event listener to choropleth layer
choroplethLayer.on('click', function(e) {
  var country = e.target.feature.properties.name;
  
  // Send AJAX request to Flask route to get travel details for country
  $.ajax({
    url: '/get_travel_details',
    data: {country: country},
    success: function(response) {
      // Display travel details in modal or popup
      // The response will be a JSON object with the travel details
    }
  });
});
