let flash = $("#flashes");
let navigation = $("#nav");
let body = $("#body");
let sideNavigation = $("#sidenav");

function isScrolledIntoView(elm) {
    let rect = elm.getBoundingClientRect();
    let viewHeight = Math.max(document.documentElement.clientHeight, window.innerHeight);
    return !(rect.bottom < 0 || rect.top - viewHeight >= 0);
}

$(document).ready(() => {
    if (document.getElementById("flashes")) {
        let flashes = flash;
        let msgHeight = flashes.innerHeight();
        let navHeight = navigation.innerHeight();
        navigation.css('top', msgHeight);
        body.css("padding-top", "0");
        flashes.css("margin-bottom", navHeight);
        sideNavigation.css('paddingTop', msgHeight + navHeight);
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
    let navHeight = navigation.innerHeight();
    flash.remove();
    navigation.css('top', 0);
    body.css("padding-top", navHeight);
    sideNavigation.css('paddingTop', navHeight);
    $(window).resize(() => {
        body.css("padding-top", navHeight);
    });
}