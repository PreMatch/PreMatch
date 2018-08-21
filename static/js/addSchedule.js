let selectedTeachers = [];

function filterTeachers(period) {
    let input, filter, a, i;
    input = document.getElementById(`teacherInput${period}`);
    filter = input.value.toUpperCase();

    let linkHolder = document.getElementById(`link-holder-${period}`);

    if (filter.length > 0) {
        linkHolder.style.display = "Block";
    } else {
        linkHolder.style.display = "None";
    }
    let div = document.getElementById(`teacher-dropdown${period}`);
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1 && filter !== '') {
            a[i].style.display = "block";
        } else {
            a[i].style.display = "none";
        }
    }
}

function selectInput(period) {
    $("#form").children().each((index) => {
        let contentDiv = document.getElementById('form').children[index].children[0];
        if (!contentDiv.id.endsWith(period)) {
            contentDiv.getElementsByTagName('div')[0].style.display = "None";
        }
    });
}

function selectTeacher(period, teacher) {
    // TODO: Some sort of visual effect, probably some sort of message

    let form = document.getElementById('form-invis');

    let input = form.querySelector(`#input-invis-${period}`);

    if (input.id.endsWith(period)) {
        input.setAttribute('value', teacher);
    }

}