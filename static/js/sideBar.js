let navOpen = false;
const sideBarWidth = 250;

let sidenav = $("#sidenav");
let overlay = $("#overlay");
let nav = $('#nav');
let navLogo = $("#nav-logo");
let navBrand = $('#navbar-brand');
let burger = $("#nav-burg");

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openNav() {
    sidenav.width(sideBarWidth);

    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            element.style.marginRight = `${sideBarWidth}px`;
        });
    }

    overlay.width($(window).width() - sideBarWidth);

    burger.addClass("is-active overridden-white");
    if ($("#body").hasClass("bg-primary")) {
        burger.css("cssText", "color: #03A9F4 !important;");
        burger.css("cssText", "color: #03A9F4 !important;");
    }
    sleep(1000);
    navOpen = true;
}

function closeNav() {
    sidenav.width(0);
    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            element.style.marginRight = "0"
        });
    }

    overlay.width(0);


    burger.removeClass("is-active overridden-white");

    if ($("#body").hasClass("bg-primary")) {
        burger.css("cssText", "color: white !important;");
    } else {
        burger.css("cssText", "");
    }
    sleep(1000);
    navOpen = false;
}

function toggleNav() {
    if (navOpen) {
        closeNav();
    } else {
        openNav();
    }
}

navLogo.width(navLogo.innerHeight());
navBrand.css('min-height', nav.innerHeight());

$(document).ready(() => {
    navLogo.width(navLogo.innerHeight());
    navBrand.css('min-height', nav.innerHeight());

    let flash = document.getElementById("flashes");

    if (!flash) {
        sidenav.css("padding-top", nav.innerHeight());
    } else {
        sidenav.css("padding-top", $(flash).innerHeight() + nav.innerHeight());
    }

    $(window).resize(() => {
        if (navOpen) {
            overlay.addClass('notransition'); // Disable transitions
            overlay.width($(window).width() - sideBarWidth);
            overlay[0].offsetHeight; // Trigger a reflow, flushing the CSS changes
            overlay.removeClass('notransition'); // Re-enable transitions
        }

        navLogo.width(navLogo.innerHeight());
        navBrand.css('min-height', nav.innerHeight());
        if (flash) {
            sidenav.css("padding-top", $(flash).innerHeight() + nav.innerHeight());
        } else {
            sidenav.css("padding-top", nav.innerHeight());
        }
    });

    $(document).click((event) => {
        if (event.target.id === "overlay") {
            closeNav();
        }
    });

    if ($("#body").hasClass("bg-primary")) {
        sidenav.css("background-color", "white");
        burger.css("cssText", "color: white !important;");

        sidenav.children('a').each((_, domChild) => {
            const child = $(domChild);

            if (child.hasClass('sidenav-active')) {
                child.css("cssText", "color: white !important; background-color: #03A9F4;");
            } else {
                child.css("cssText", "color: #03A9F4 !important;");
            }
        });
    }
});
