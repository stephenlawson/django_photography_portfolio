//navbar
const navToggle = document.querySelector(".nav-toggle")
const links = document.querySelector(".links")

navToggle.addEventListener("click", function () {
  links.classList.toggle("show-links")
})




//dark mode

let icon = document.getElementById("dark-mode-icon")
let mode = localStorage.getItem("dark-mode")
let invert = localStorage.getItem("invert")
if (mode == "dark-mode" && invert == "invert"){
  document.documentElement.classList.toggle("dark-mode")
  document.querySelectorAll('.inverted').forEach((result) => {
    result.classList.toggle('invert')
  })
}else{
  // pass
}


function darkmodeFunction(){
  console.log('test')
  document.documentElement.classList.toggle("dark-mode")
  localStorage.setItem("dark-mode", "dark-mode")
  if(document.documentElement.classList.contains("dark-mode")){
    icon.src = "https://django-portfolio-apps.s3.amazonaws.com/photo_app/img/sun.png"
  }else{
    icon.src = "https://django-portfolio-apps.s3.amazonaws.com/photo_app/img/moon.png"
    localStorage.removeItem("dark-mode")
    localStorage.removeItem("invert")
  }
  document.querySelectorAll('.inverted').forEach((result) => {
    result.classList.toggle('invert')
    localStorage.setItem("invert", "invert")
  })
}  

// gallery js

var modal = document.getElementById('photo-modal');
var modalImg = document.getElementById('photo-modal-img');
var closeBtn = document.getElementById('photo-modal-close');
var commentForm = document.getElementById('comment-form');
var commentSection = document.getElementById('comment-section');
//var isLiked = thumbnail.dataset.liked.toString().trim().toLowerCase() === 'true';
//updateLikeButton(isLiked);

function fetchComments(photoId) {
    fetch('/get_comments/' + photoId + '/')
        .then(response => response.json())
        .then(data => {
            commentSection.innerHTML = '';
            data.comments.forEach(comment => {
                var commentItem = document.createElement('div');
                commentItem.classList.add('comment-item');
                commentItem.innerHTML = `
                    <span>${comment.user}</span>
                    <span>${comment.timestamp}</span>
                    <p>${comment.content}</p>
                `;
                commentSection.appendChild(commentItem);
            });
        })
        .catch(error => console.error(error));
}

function addComment(photoId, content) {
    var form = new FormData();
    var csrftoken = getCookie('csrftoken')
    form.append('comment', content);
    console.log(photoId);
    fetch('/add_comment/' + photoId + '/', {
        method: 'POST',
        body: form,
        headers: {
            'X-CSRFToken': csrftoken
        }
    })
        .then(response => response.json())
        .then(data => {
            // Update the comment section
            fetchComments(photoId);
        })
        .catch(error => console.error(error));
}

function updateLikeButton(isLiked) {
    const likeButton = document.getElementById('like-button');
    const likeIcon = document.getElementById('like-icon');
    console.log(isLiked);
    var isLikedstr = isLiked.toString().trim().toLowerCase();
    console.log(isLikedstr);
    if (isLikedstr === 'true') {
        console.log('liked');
        likeButton.classList.add('liked');
        likeIcon.classList.remove('far');
        likeIcon.classList.add('fas');
        likeIcon.style.color = 'red';
    } else {
        console.log('not liked');
        likeButton.classList.remove('liked');
        likeIcon.classList.remove('fas');
        likeIcon.classList.add('far');
        likeIcon.style.color = 'black';
    }
}

const thumbnails = document.getElementsByClassName('photo-thumbnail');
Array.from(thumbnails).forEach(function (thumbnail) {
    thumbnail.addEventListener('click', function (event) {
        modal.style.display = 'block';
        modalImg.src = thumbnail.src;
        modalImg.alt = thumbnail.dataset.src;
        var photoId = thumbnail.dataset.src;
        modalImg.src = thumbnail.src.replace('_thumb', '_full');
        fetchComments(photoId);

        // Check the initial liked status from the model and update the like button UI
        var isLiked = thumbnail.dataset.liked;
        console.log('database liked is: ',thumbnail.dataset.liked);
        console.log(isLiked);
        updateLikeButton(isLiked);
    });
});

closeBtn.onclick = function() {
    modal.style.display = 'none';
};

$(document).ready(function() {
    var modal = document.getElementById("photo-modal");
    var modalImg = document.getElementById("photo-modal-img");
    var thumbnails = document.getElementsByClassName("photo-thumbnail");
    var currentIndex = 0;

    // Variables for swipe gesture
    var touchstartX = 0;
    var touchendX = 0;

    // Navigate to previous photo
    $("#prev-photo").click(function() {
        navigatePrevious();
    });

    // Navigate to next photo
    $("#next-photo").click(function() {
        navigateNext();
    });

    modalImg.addEventListener('touchstart', function(event) {
        touchstartX = event.touches[0].screenX;
    });

    modalImg.addEventListener('touchmove', function(event) {
        touchendX = event.touches[0].screenX;
    });

    modalImg.addEventListener('touchend', function(event) {
        handleSwipe();
    });

    function handleSwipe() {
        var minSwipeDistance = 50; // Minimum distance to trigger a swipe
        var swipeDistance = touchendX - touchstartX;

        if (Math.abs(swipeDistance) >= minSwipeDistance) {
            if (swipeDistance > 0) {
                navigatePrevious();
            } else {
                navigateNext();
            }
        }
    }

    function navigateNext() {
        currentIndex = (currentIndex + 1) % thumbnails.length;
        var photoId = thumbnails[currentIndex].alt; // Get the photo ID of the next photo
        updateModalContent(photoId);
    }
    
    function navigatePrevious() {
        currentIndex = (currentIndex - 1 + thumbnails.length) % thumbnails.length;
        var photoId = thumbnails[currentIndex].alt; // Get the photo ID of the previous photo
        updateModalContent(photoId);
    }
    
    function updateModalContent(photoId) {
        var currentImageNumber = currentIndex + 1;
        var totalImagesNumber = thumbnails.length;
        document.getElementById("photo-count").textContent = currentImageNumber + " / " + totalImagesNumber;
    
        var nextImage = new Image();
        nextImage.src = thumbnails[currentIndex].src.replace('_thumb', '_full');
        nextImage.onload = function() {
            modalImg.src = nextImage.src;
            modalImg.alt = thumbnails[currentIndex].alt;
            modalImg.style.transition = 'transform 0.5s ease';
            modalImg.style.transform = 'translateX(100%)';
            setTimeout(function() {
                modalImg.style.transition = '';
                modalImg.style.transform = 'translateX(0)';
            }, 50);
        };
    
        // Fetch comments and likes for the current photo using AJAX
        fetchCommentsLikes(photoId);
    }

    // Function to fetch comments and likes for a photo using AJAX
    function fetchCommentsLikes(photoId) {
        fetch('/get_comments/' + photoId + '/')
            .then(response => response.json())
            .then(data => {
                console.log('Comments data:', data);
                var commentSection = document.getElementById("comment-section");
                commentSection.innerHTML = ''; // Clear existing comments
    
                data.comments.forEach(comment => {
                    var commentItem = document.createElement('div');
                    commentItem.classList.add('comment-item');
                    commentItem.innerHTML = `
                        <span>${comment.user}</span>
                        <span>${comment.timestamp}</span>
                        <p>${comment.content}</p>
                    `;
                    commentSection.appendChild(commentItem);
                });
            })
            .catch(error => console.error(error));
    
        fetch('/get_like_status/' + photoId + '/')
            .then(response => response.json())
            .then(data => {
                console.log('Like status data:', data);
                updateLikeButton(data.is_liked);
            })
            .catch(error => console.error(error));
    }

    // Function to extract the photo ID from the current image alt attribute
    function getCurrentPhotoId() {
        return modalImg.alt;
    }

    // Function to update the like button based on the current like status
    function updateLikeButton(isLiked) {
        const likeButton = document.getElementById('like-button');
        const likeIcon = document.getElementById('like-icon');
        if (isLiked) {
            likeButton.classList.add('liked');
            likeIcon.classList.remove('far');
            likeIcon.classList.add('fas');
            likeIcon.style.color = 'red';
        } else {
            likeButton.classList.remove('liked');
            likeIcon.classList.remove('fas');
            likeIcon.classList.add('far');
            likeIcon.style.color = 'black';
        }
    }

    // Set initial currentIndex when clicking on a thumbnail
    Array.from(thumbnails).forEach(function(thumbnail, index) {
        thumbnail.addEventListener('click', function() {
            currentIndex = index;
            updateModalContent();
        });
    });
});



window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

commentForm.addEventListener('submit', function(event) {
    event.preventDefault();
    var photoId = modalImg.alt;
    var commentInput = document.getElementById('comment-input');
    var content = commentInput.value;
    addComment(photoId, content);
    commentInput.value = '';
});

function getCookie(name) {
    const cookieValue = document.cookie.split('; ')
        .find(cookie => cookie.startsWith(name + '='))
        .split('=')[1];
    return decodeURIComponent(cookieValue);
}

function toggleLikeStatus(photoId) {
    fetch(`/toggle_like_status/${photoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
        .then(response => response.json())
        .then(data => {
            const isLiked = data.is_liked;
            updateLikeButton(isLiked);
        })
        .catch(error => console.error(error));
}

const likeButton = document.getElementById('like-button');
likeButton.addEventListener('click', function(event) {
    event.preventDefault();
    var photoId = modalImg.alt;
    toggleLikeStatus(photoId);
});

// Get all elements with class="closebtn"
var close = document.getElementsByClassName("closebtn");
var i;

// Loop through all close buttons
for (i = 0; i < close.length; i++) {
  // When someone clicks on a close button
  close[i].onclick = function(){

    // Get the parent of <span class="closebtn"> (<div class="alert">)
    var div = this.parentElement;

    // Set the opacity of div to 0 (transparent)
    div.style.opacity = "0";

    // Hide the div after 600ms (the same amount of milliseconds it takes to fade out)
    setTimeout(function(){ div.style.display = "none"; }, 600);
  }
}



// Get the button element
var buttonAppt = document.querySelector(".widget-book-appointment-button");

// Add click event listener
buttonAppt.addEventListener('click', function() {
  // Open a new page
  console.log("clicked");
  window.open('/thank-you-for-booking', '_blank');

  // Track ad click-through (replace with your tracking code)
  // Example: trackAdClickThrough();
});

for (let i = 1; i <= 19; i++) {
    let selector = `.blurred-img .port-${i}`;
    let url = `https://django-portfolio-apps.s3.amazonaws.com/photo_app/img/port-${i}-small.jpg`;
    let style = `background-image: url("${url}");`;
    let css = `${selector} { ${style} }`;
    console.log(css);
  }

const blurredImageDiv = document.querySelectorAll(".blurred-img")
blurredImageDiv.forEach(div => {
    const img = div.querySelector("img")

    function loaded() {
        div.classList.add("loaded")
    }
    if (img.complete) {
        loaded()
      } else {
        img.addEventListener("load", loaded)
      }
})

document.addEventListener("DOMContentLoaded", function () {
    const loginContainer = document.querySelector(".login-container");
    const highResImage = new Image();
    highResImage.src = "https://django-portfolio-apps.s3.amazonaws.com/photo_app/img/header-banner.jpg";

    highResImage.onload = function () {
        loginContainer.style.backgroundImage = `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.3)), url('${highResImage.src}') right/cover no-repeat fixed`;
    };
});

// Hover effect in blog posts list

document.getElementById("cards").onmousemove = e => {
    for(const card of document.getElementsByClassName("card")) {
      const rect = card.getBoundingClientRect(),
            x = e.clientX - rect.left,
            y = e.clientY - rect.top;
  
      card.style.setProperty("--mouse-x", `${x}px`);
      card.style.setProperty("--mouse-y", `${y}px`);
    };
  }

// Initialize Owl Carousel after the document is ready
$(document).ready(function() {
    // Check if the element with ID "reviews-carousel" exists
    var reviewsCarousel = $('#reviews-carousel');
    if (reviewsCarousel.length > 0) {
        // Initialize Owl Carousel only if the element exists
        reviewsCarousel.owlCarousel({
            loop: true,
            margin: 10,
            nav: true,
            dots: false,
            responsive: {
                0: {
                    items: 1
                },
                600: {
                    items: 3
                },
                1000: {
                    items: 5
                }
            }
        });
    }
});

