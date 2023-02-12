function changeViewMode() {
  if (window.innerWidth < 767) {
    document.body.classList.add("mobile-mode");
    changeElementMode();
  } else {
    // desktop or tablet screen, change view mode to desktop
    document.body.classList.remove("mobile-mode");
  }
}

function changeElementMode() {
  div.classList.remove('new-class');
  div.classList.toggle('new-class');

  div.classList.remove('new-class');
  div.classList.toggle('new-class');

  div.classList.remove('new-class');
  div.classList.toggle('new-class');
}



// Call the changeViewMode function when the page loads
window.addEventListener("load", changeViewMode);

// Call the changeViewMode function whenever the screen is resized
window.addEventListener("resize", changeViewMode);