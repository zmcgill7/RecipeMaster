var images = document.querySelectorAll('.carousel-slider img');
var dots = document.querySelectorAll('.dot');
var currentImg = 0; //index of first image
const interval = 3000; // speed of slides

function changeSlide(n) {
    // function to change the image using the dots
    for (var i=0; i < images.length; i++) {
        images[i].style.opacity = 0;
        if (dots[i]) {
            dots[i].className = dots[i].className.replace('active', '');
        }
    }

    currentImg = (currentImg + 1) % images.length; // update the index number
    if (n != undefined) {
        clearInterval(timer);
        timer = setInterval(changeSlide, interval);
        currentImg = n;
    }
    images[currentImg].style.opacity = 1;
    if (dots[currentImg]) {
        dots[currentImg].className += ' active';
    }
}

function showSlides(n) {
    var nextImg = currentImg + n;
    if (nextImg < 0) {
        nextImg = images.length - 1;
    }
    if (nextImg >= images.length) {
        nextImg = 0;
    }
    changeSlide(nextImg);
}

// make slides change automatically
var timer = setInterval(changeSlide, interval)
