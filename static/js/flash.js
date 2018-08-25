function isScrolledIntoView(elm) {
  var rect = elm.getBoundingClientRect();
  var viewHeight = Math.max(document.documentElement.clientHeight, window.innerHeight);
  return !(rect.bottom < 0 || rect.top - viewHeight >= 0);
}

$(document).ready(() => {
    if (document.getElementById("flashes")) {
        let flashes = $("#flashes");
        let msgHeight = flashes.innerHeight();
        document.getElementById("nav").style.top = `${msgHeight}px`;
        $("#body").css("padding-top", "0");
        flashes.css("margin-bottom", $("#nav").innerHeight());
        document.getElementById("sidenav").style.paddingTop = `${msgHeight + $("#nav").innerHeight()}px`;
        flashes.css('display', 'block');
        $(window).scroll(() => {
            if(document.getElementById("flashes")) {
                if (!isScrolledIntoView(document.getElementById("flashes"))) {
                    closeFlash();
                }
            }
        });
    }

});

function closeFlash() {
    $("#flashes").remove();
    document.getElementById("nav").style.top = "0";
    let navHeight = $("#nav").innerHeight();
    $("#body").css("padding-top", navHeight);
    document.getElementById("sidenav").style.paddingTop = `${navHeight}px`;
    $(window).resize(() => {
        $("#body").css("padding-top", $("#nav").innerHeight());
    });
}