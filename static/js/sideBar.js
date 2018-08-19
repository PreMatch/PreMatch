let navOpen = false;
const sideBarWidth = 200;

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

function openNav() {
    $("#sidenav").width(sideBarWidth);
    document.getElementById("main").style.marginRight = `${sideBarWidth}px`;
    $(".navbar-burger:first").addClass("is-active overridden-white");
    sleep(1000);
    navOpen = true;
}

function closeNav() {
    $("#sidenav").width(0);
    document.getElementById("main").style.marginRight = "0";
    $(".navbar-burger:first").removeClass("is-active overridden-white");
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