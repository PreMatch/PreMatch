function setActive(href) {
    let sidenav = document.getElementById('sidenav');
    let links = sidenav.children;
    let activeIndex = -1;
    for (let i = 0; i < links.length; i++) {
        let currentLink = links[i];
        if (currentLink.getAttribute("href") === href) {
            currentLink.classList.add("sidenav-active");
            activeIndex = i;
            break;
        }
    }

    for (let i = 0; i < links.length; i++) {
        if (i !== activeIndex)
            links[i].classList.add("overridden-white");
    }
}