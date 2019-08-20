let flashParent = $("#flashes");
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
        let flashes = flashParent;
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
                $('.flash').each((index, flash) => {
                    if(!isScrolledIntoView(flash)) {
                        closeFlash(parseInt($(flash).attr('id').split('-')[1]));
                    }
                });
            }
        });
    }

});

function closeFlash(index) {
    let flash = $(`#flash-${index}`);

    if (flash.length > 0) {

        let navHeight = navigation.innerHeight();
        flash.remove();

        let remainingFlashHeight = 0;

        if ($('.flash').length === 0) {
            flashParent.remove();
        } else {
            remainingFlashHeight = flashParent.innerHeight();
        }


        navigation.css('top', remainingFlashHeight);
        body.css("padding-top", remainingFlashHeight === 0 ? navHeight : 0);
        sideNavigation.css('paddingTop', navHeight + remainingFlashHeight);
        $(window).resize(() => {
            body.css("padding-top", remainingFlashHeight === 0 ? navHeight : 0);
        });
    }
}