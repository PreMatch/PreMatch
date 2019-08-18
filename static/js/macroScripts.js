function setActive(href) {
    let sidenav = document.getElementById('sidenav-link-container');
    let links = sidenav.children;
    let activeIndex = -1;
    for (let i = 0; i < links.length; i++) {
        let currentLink = links[i];
        if (currentLink.getAttribute("href") === href) {
            currentLink.classList.add("sidenav-active");

            if($('#body').hasClass('bg-primary'))
                currentLink.classList.add('inverted');

            activeIndex = i;
            break;
        }
    }

    for (let i = 0; i < links.length; i++) {
        if (i !== activeIndex && !$('#body').hasClass('bg-primary'))
            links[i].classList.add("overridden-white");
    }

    if (!$('#body').hasClass('bg-primary')) {
        $('#nav-bottom-links').children('ul').first().children('li').each((indx, li) => {
            $(li).children('a').each((index, link) => {
                $(link).addClass('overridden-white');
            });
        });
    }
}