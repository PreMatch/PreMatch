$(document).ready(() => {

    if (document.getElementById("flashes")) {
        let msgHeight = $("#flashes").innerHeight();
        document.getElementById("nav").style.top = `${msgHeight}px`;
        $("#body").css("padding-top", "0");
        $("#flashes").css("margin-bottom", $("#nav").innerHeight());
        document.getElementById("sidenav").style.paddingTop = `${msgHeight + $("#nav").innerHeight()}px`;
    }

});

function closeFlash() {
    $("#flashes").remove();
    document.getElementById("nav").style.top = "0";
    let navHeight = $("#nav").innerHeight();
    $("#body").css("padding-top", navHeight);
    document.getElementById("sidenav").style.paddingTop = `${navHeight}px`;
}