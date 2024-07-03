// --------- Preview image after upload ---------
function previewImageReuse(event, clsName) {
    const id = $(this);
    const reader = new FileReader();
    reader.onload = function(event) {
        $('.uploadedImage').remove();
        $($.parseHTML('<img width="100%" class="uploadedImage" height="410px">'))
                .attr('src', event.target.result).prependTo(`.${clsName}`);
    }

    reader.readAsDataURL(event.target.files[0]);
}

// Preview multiple images after upload
function previewMultipleImages(input, placeToInsertImagePreview) {
    var filesAmount = input.files.length;
    if (input.files.length > 0) {
        for (i = 0; i < filesAmount; i++) {
            var reader = new FileReader();

            reader.onload = function(event) {
                $($.parseHTML('<img width="180px" class="p-1" >'))
                .attr('src', event.target.result).prependTo(`.${placeToInsertImagePreview}`);
            }
            reader.readAsDataURL(input.files[i]);
        }
    } else {
        $('div.displayImg').html('No image selected');
    }
}

// --------- Responsive-navbar -----------
let menuIcon = document.querySelector('.menuIcon');
let nav = document.querySelector('.overlay-menu');

menuIcon.addEventListener('click', () => {
    if (nav.style.transform != 'translateX(0%)') {
        nav.style.transform = 'translateX(0%)';
        nav.style.transition = 'transform 0.2s ease-out';
    } else {
        nav.style.transform = 'translateX(-100%)';
        nav.style.transition = 'transform 0.2s ease-out';
    }
});

// Toggle Menu Icon ========================================
let toggleIcon = document.querySelector('.menuIcon');
toggleIcon.addEventListener('click', () => {
    if (toggleIcon.className != 'menuIcon toggle') {
        toggleIcon.className += ' toggle';
    } else {
        toggleIcon.className = 'menuIcon';
    }
});

// Get seconds from time ========================================
function timeToSeconds(timeStr) {
    var parts = timeStr.split(':');
    if (parts.length === 3) {
        var hours = parseInt(parts[0]);
        var minutes = parseInt(parts[1]);
        var seconds = parseInt(parts[2]);
        if (!isNaN(hours) && !isNaN(minutes) && !isNaN(seconds)) {
            return hours * 3600 + minutes * 60 + seconds;
        }
    } else if (parts.length === 2) {
        var minutes = parseInt(parts[0]);
        var seconds = parseInt(parts[1]);
        if (!isNaN(minutes) && !isNaN(seconds)) {
            return minutes * 60 + seconds;
        }
    } else {
        var seconds = parseInt(parts[0]);
        if (!isNaN(seconds)) {
            return seconds;
        }
    }

    return NaN; // Return NaN if the time string is invalid
}


// Sweet alert success functions
function success_operation(msg) {
    // Success alert auto close
    const Toast = Swal.mixin({
        toast: true,
        timer: 4000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    });
    Toast.fire({
        icon: 'success',
        title: '<span style="color:#f5f5f5">' + msg + '</span>',
        background: 'rgb(51, 153, 102, 0.97)',
    });
}
// Sweet alert error functions
function error_operation(msg) {
    // Error alert auto close
    const Toast = Swal.mixin({
        toast: true,
        timer: 4000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.addEventListener('mouseenter', Swal.stopTimer)
            toast.addEventListener('mouseleave', Swal.resumeTimer)
        }
    });
    Toast.fire({
        icon: 'error',
        title: '<span style="color:#f5f5f5">' + msg + '</span>',
        background: 'rgba(187, 57, 57, 0.89)',
    });
}