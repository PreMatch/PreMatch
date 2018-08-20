if (document.getElementById("login-message")) {
    let msgHeight = $("#login-message").innerHeight();
    console.log(msgHeight, document.getElementById("nav"));
    document.getElementById("nav").style.top = `${msgHeight}px`;
    $("#body").css("padding-top", "0");
    document.getElementById("sidenav").style.paddingTop = `${msgHeight + $("#nav").innerHeight()}px`;
}

function closeLoginMessage() {
    $("#login-message").remove();
    document.getElementById("nav").style.top = "0";
    let navHeight = $("#nav").innerHeight();
    $("#body").css("padding-top", navHeight);
    document.getElementById("sidenav").style.paddingTop = `${navHeight}px`
}