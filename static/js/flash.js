let flash = $("#flashes");
let nav = $("#nav");
let body = $("#body");
let sidenav = $("#sidenav");

function isScrolledIntoView(elm) {
    let rect = elm.getBoundingClientRect();
    let viewHeight = Math.max(document.documentElement.clientHeight, window.innerHeight);
    return !(rect.bottom < 0 || rect.top - viewHeight >= 0);
}

$(document).ready(() => {
    if (document.getElementById("flashes")) {
        let flashes = flash;
        let msgHeight = flashes.innerHeight();
        let navHeight = nav.innerHeight();
        nav.css('top', msgHeight);
        body.css("padding-top", "0");
        flashes.css("margin-bottom", navHeight);
        sidenav.css('paddingTop', msgHeight + navHeight);
        flashes.css('display', 'block');
        $(window).scroll(() => {
            let flashDOM = document.getElementById("flashes");
            if (flashDOM) {
                if (!isScrolledIntoView(flashDOM)) {
                    closeFlash();
                }
            }
        });
    }

});

function closeFlash() {
    let navHeight = nav.innerHeight();
    flash.remove();
    nav.css('top', 0);
    body.css("padding-top", navHeight);
    sidenav.css('paddingTop', navHeight);
    $(window).resize(() => {
        body.css("padding-top", navHeight);
    });
}