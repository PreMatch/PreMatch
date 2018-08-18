let navOpen = false;

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openNav() {
    $("#sidenav").width(250);
    document.getElementById("main").style.marginRight = "250px";
    $(".navbar-burger:first").addClass("is-active overridden-white");
    navOpen = true;
}

function closeNav() {
    $("#sidenav").width(0);
    document.getElementById("main").style.marginRight = "0";
    $(".navbar-burger:first").removeClass("is-active overridden-white");
    navOpen = false;
}

function toggleNav() {
    if (navOpen) {
        closeNav();
    } else {
        openNav();
    }
}