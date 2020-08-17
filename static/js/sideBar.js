let navOpen = false;
const sideBarWidth = 270;

let sidenav = $("#sidenav");
let overlay = $("#overlay");
let nav = $('#nav');
let navLogo = $("#nav-logo");
let navBrand = $('#navbar-brand');
let burger = $("#nav-burg");
let sideBurger = $('#nav-burg-sidenav');

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openNav() {
    sidenav.width(sideBarWidth);

    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            if (element.tagName.toLowerCase() !== 'iframe') {
                element.setAttribute('data-initial-margin-right', element.style.marginRight);
                element.style.marginRight = `${sideBarWidth}px`;
            } else {
                let width = $(element).innerWidth();
                let height = $(element).innerHeight();

                let ratio = width / height;

                element.style.padding = `${sideBarWidth * (1 / ratio) / 2}px ${sideBarWidth}px ${sideBarWidth * (1 / ratio) / 2}px 0`;
            }
        });
    }

    overlay.width($(window).width() - sideBarWidth);

    sideBurger.addClass("is-active overridden-white");
    burger.addClass("is-active overridden-white");
    burger.hide();
    if ($("#body").hasClass("bg-primary")) {
        burger.css("cssText", "color: #03A9F4 !important;");
        sideBurger.css("cssText", "color: #03A9F4 !important;");
    }
    sleep(1000);
    navOpen = true;
}

function closeNav() {
    sidenav.width(0);
    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            if (element.tagName.toLowerCase() !== 'iframe') {

                element.style.marginRight = element.getAttribute('data-initial-margin-right');
            } else {
                element.style.padding = '0';
            }
        });
    }

    overlay.width(0);

    sideBurger.removeClass("is-active overridden-white");
    burger.removeClass("is-active overridden-white");
    sideBurger.hide();
    burger.show();

    if ($("#body").hasClass("bg-primary")) {
        burger.css("cssText", "color: white !important;");
        sideBurger.css("cssText", "color: white !important;");
    } else {
        burger.css("cssText", "");
        sideBurger.css("cssText", "");
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

    $(window).bind('resize', () => {
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

        $("#body").css("padding-top", $("#nav").innerHeight());

        $(document).ready(() => {

            if (document.getElementById("flashes")) {
                const $flashes = $("#flashes");
                const $nav = $("#nav");

                let msgHeight = $flashes.innerHeight();
                document.getElementById("nav").style.top = `${msgHeight}px`;
                $("#body").css("padding-top", "0");
                $flashes.css("margin-bottom", $nav.innerHeight());
                document.getElementById("sidenav").style.paddingTop = `${msgHeight + $nav.innerHeight()}px`;
                $flashes.css('display', 'block');
            } else {
                $(window).resize(() => {
                    $("#body").css("padding-top", $("#nav").innerHeight());
                });
            }
        });

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
