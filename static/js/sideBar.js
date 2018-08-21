let navOpen = false;
const sideBarWidth = 250;

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openNav() {
    $("#sidenav").width(sideBarWidth);

    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            element.style.marginRight = `${sideBarWidth}px`
        });
    }

    $("#overlay").width($(window).width() - sideBarWidth);

    $(".navbar-burger:first").addClass("is-active overridden-white");
    if ($("#body").hasClass("bg-primary")) {
        $(".navbar-burger:first").css("cssText", "color: #03A9F4 !important;")
    }
    sleep(1000);
    navOpen = true;
}

function closeNav() {
    $("#sidenav").width(0);
    let pushed = document.getElementsByClassName("pushed");

    if ($(window).width() > 510) {
        Array.prototype.forEach.call(pushed, (element) => {
            element.style.marginRight = "0"
        });
    }

    $("#overlay").width(0);


    $(".navbar-burger:first").removeClass("is-active overridden-white");

    if ($("#body").hasClass("bg-primary")) {
        $("#nav-burg").css("cssText", "color: white !important;");
    } else {
        $("#nav-burg").css("cssText", "");
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

$(document).ready(() => {

    $("#nav-logo").width($("#nav-logo").innerHeight());

    if (!document.getElementById("login-message")) {
        $("#sidenav").css("padding-top", $("#nav").innerHeight());
    }

    $(window).resize(() => {
        if (navOpen) {
            $("#overlay").width($(window).width() - sideBarWidth);
        }
    });

    $(document).click((event) => {
        if (event.target.id === "overlay") {
            closeNav();
        }
    });

    if ($("#body").hasClass("bg-primary")) {
        $("#sidenav").css("background-color", "white");
        $("#nav-burg").css("cssText", "color: white !important;");

        $("#sidenav").children('a').each((_, domChild) => {
            const child = $(domChild);

            if (child.hasClass('sidenav-active')) {
                child.css("cssText", "color: white !important; background-color: #03A9F4;");
            } else {
                child.css("cssText", "color: #03A9F4 !important;");
            }
        });
    }
});
