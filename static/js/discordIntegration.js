let bgColors = ['#f04747', '#faa61a', '#7289da', '#747f8d', '#43b581'];
let names = ["Anakin Skywalker", "Luke Skywalker", "Darth Vader", "Obi-Wan Kenobi", "Leia Organa", "R2-D2", "C-3PO", "Chewbacca", "Han Solo", "Darth Maul"];
let otherIds = [];

function getRandomInt(max) {
    return Math.floor(Math.random() * Math.floor(max));
}

function generateUsers() {
    Array.prototype.forEach.call(document.getElementsByClassName('other-user'), (userCont) => {
        let pic = userCont.getElementsByTagName('img')[0];
        pic.style.backgroundColor = bgColors[getRandomInt(bgColors.length)];
        let name = userCont.getElementsByClassName('username')[0];
        let namesId = getRandomInt(names.length);
        name.innerHTML = names[namesId];
        names.splice(namesId, 1);
        let userId = document.getElementById('user-id').innerHTML.substr(1);
        let id = '';
        while (true) {
            for (let i = 0; i < 4; i++) {
                id += getRandomInt(10);
            }

            if (id === userId || otherIds.includes(id)) {
                id = '';
                continue;
            }

            otherIds.push(id);
            break;
        }

        let idText = userCont.getElementsByClassName('id')[0];
        idText.innerHTML = "#" + id;
    });

    names = ["Anakin Skywalker", "Luke Skywalker", "Darth Vader", "Obi-Wan Kenobi", "Leia Organa", "R2-D2", "C-3PO", "Chewbacca", "Han Solo", "Darth Maul"]; //Reset array
}

function manageChain() {
    let chain = $('#chain');
    let userBox = $('#user-box');
    let prematchName = $('#prematch-name');
    let offset = userBox.offset();

    let top = offset.top + userBox.innerHeight() / 4;
    let left = offset.left + userBox.innerWidth() + 10;

    let prematchLeft = prematchName.offset().left - 10;

    let width = prematchLeft - left;

    chain.css({
        'top': top,
        'left': left,
        'width': width
    });
}

generateUsers();
manageChain();

$(window).resize(() => manageChain());