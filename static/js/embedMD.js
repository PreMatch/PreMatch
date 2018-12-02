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
}