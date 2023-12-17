(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('d-flex');
                $('#spinner').addClass("d-none")
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 45) {
            $('.navbar').addClass('sticky-top shadow-sm');
        } else {
            $('.navbar').removeClass('sticky-top shadow-sm');
        }
    });
    
    
    // Dropdown on mouse hover
    const $dropdown = $(".dropdown");
    const $dropdownToggle = $(".dropdown-toggle");
    const $dropdownMenu = $(".dropdown-menu");
    const showClass = "show";
    
    $(window).on("load resize", function() {
        if (this.matchMedia("(min-width: 992px)").matches) {
            $dropdown.hover(
            function() {
                const $this = $(this);
                $this.addClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "true");
                $this.find($dropdownMenu).addClass(showClass);
            },
            function() {
                const $this = $(this);
                $this.removeClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "false");
                $this.find($dropdownMenu).removeClass(showClass);
            }
            );
        } else {
            $dropdown.off("mouseenter mouseleave");
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav : false,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });
    
})(jQuery);

function sign_out() {
    $.removeCookie("mytoken", { path: "/" });
    alert("Logged out!");
    window.location.href = "/";
    // Swal.fire({
    //     icon: 'success',
    //     title: 'Logged Out!',
    //     text: 'You have been successfully logged out.',
    //     showConfirmButton: false,
    //     timer: 2000, // Adjust the timer value (in milliseconds) as needed
    //     onClose: function() {
    //         window.location.reload();
    //     }
    // });
}

function searc1(event) {
    if (event.keyCode === 13) {
        let searchQuery = $('#searchInput').val();
        let url = '/search?q=' + encodeURIComponent(searchQuery);

        $.ajax({
            url: url,
            method: 'GET',
            success: function (response) {
                let wisataList = response;
                // Clear the existing content
                $('#wisata-list').empty();
                if (wisataList.length === 0) {
                    $('#wisata-list').append('<div class="container"><section class="hero is-fullwidth is-bold"><div class="hero-body"><div class="container has-text-centered"><h1 class="title">Oops!!</h1><h2 class="subtitle">Pencarian tidak ditemukan</h2></div></div></section></div>');
                } else {
                    for (let i = 0; i < wisataList.length; i++) {
                        let attraction = wisataList[i];
                        let html = '<div class="column is-3"><div class="card is-shady" style="height: 400px; border-radius: 20px;"><div class="card-image has-text-centered"><img src="/'+ attraction.image_wisata +'" alt="Image 3" class="is-3by2" style="width: 100%; height: 200px; object-fit: cover; border-radius: 20px 20px 0 0;"></div><div class="card-content"><div class="content"><h4>' + attraction.name + '</h4><p>' + attraction.description + '</p><p><a href="/wisata/' + attraction.id + '">Cek Selengkapnya</a></p></div></div></div></div>';
                        $('#wisata-list').append(html);
                    }
                }
            }
        });
    }

}

function search2(event) {
    if (event.keyCode === 13) {
        let searchQuery = $('#searchInput').val();
        let url = '/search?q=' + encodeURIComponent(searchQuery);

        $.ajax({
            url: url,
            method: 'GET',
            success: function (response) {
                let wisataList = response;
                // Clear the existing content
                $('#wisata-list').empty();
                if (wisataList.length === 0) {
                    $('#wisata-list').append('<div class="container"><section class="hero is-fullwidth is-bold"><div class="hero-body"><div class="container has-text-centered"><h1 class="title">Oops!!</h1><h2 class="subtitle">Pencarian tidak ditemukan</h2></div></div></section></div>');
                } else {
                    for (let i = 0; i < wisataList.length; i++) {
                        let attraction = wisataList[i];
                        let html = '<div class="column is-3"><div class="card is-shady" style="height: 400px; border-radius: 20px;"><div class="card-image has-text-centered"><img src="/'+ attraction.image_wisata +'" alt="Image 3" class="is-3by2" style="width: 100%; height: 200px; object-fit: cover; border-radius: 20px 20px 0 0;"></div><div class="card-content"><div class="content"><h4>' + attraction.name + '</h4><p>' + attraction.description + '</p><p><a href="/wisata/' + attraction.id + '">Cek Selengkapnya</a></p></div></div></div></div>';
                        $('#wisata-list').append(html);
                    }
                }
            }
        });
    }

}

