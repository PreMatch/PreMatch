let converter = new showdown.Converter();

function embedMD(path, id) {
    readMD(path, id)
}

function readMD(file, embedId) {
    let rawFile = new XMLHttpRequest();
    rawFile.open("GET", file, false);
    rawFile.onreadystatechange = function () {
        if (rawFile.readyState === 4) {
            if (rawFile.status === 200 || rawFile.status === 0) {
                embedHTML(converter.makeHtml(rawFile.responseText), embedId);
            }
        }
    };

    rawFile.send(null);
}

function embedHTML(html, id) {
    $(`#${id}`).append(html);
    applyClassesToMD(id);
}

function applyClassesToEach() {
    arguments[0].each((indx, element) => {
        for (let i = 1; i < arguments.length; i++) {
            $(element).addClass(arguments[i]);
        }
    });
}


function applyClassesToMD(id) {
    let document = $(`#${id}`);
    applyClassesToEach(document.children('h1'), 'title', 'is-size-1');
    applyClassesToEach(document.children('h2'), 'subtitle', 'is-size-3');
    applyClassesToEach(document.children('h3'), 'subtitle', 'is-size-5');
}