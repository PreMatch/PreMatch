let originalMargin = 0;

function filterTeachers(period) {
    let input, filter, a, i;
    input = document.getElementById(`teacherInput${period}`);
    filter = input.value.toUpperCase();

    let linkHolder = document.getElementById(`link-holder-${period}`);

    let noResultsText = document.getElementById(`no-results-${period}`);
    noResultsText.style.display = "none";

    if (filter.length > 0) {
        linkHolder.style.display = "Block";
        let div = document.getElementById(`teacher-dropdown-${period}`);
        a = div.getElementsByTagName("a");

        let hitCounter = 0;

        for (i = 0; i < a.length; i++) {
            if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1 && filter !== '') {
                a[i].style.display = "block";
                hitCounter++;
            } else {
                a[i].style.display = "none";
            }
        }

        if (hitCounter === 0 && filter.length > 0) {
            noResultsText.style.display = "block";
        }

        let container = document.getElementById(`dropdown-container-${period}`);
        if ($(linkHolder).innerHeight() > 0) {
            $(container).css('margin-bottom', originalMargin + $(linkHolder).innerHeight());
        }

    } else {
        linkHolder.style.display = "None";
        $(document.getElementById(`dropdown-container-${period}`)).css('margin-bottom', originalMargin);
    }

}

function selectInput(period) {
    $("#form").children().each((index) => {
        if (document.getElementById('form').children[index].tagName === "DIV") {
            let contentDiv = document.getElementById('form').children[index].children[0];
            if (!contentDiv.id.endsWith(period)) {
                contentDiv.getElementsByTagName('div')[0].style.display = "None";
                let container = document.getElementById(`dropdown-container-${contentDiv.id.slice(-1)}`);
                $(container).css('margin-bottom', originalMargin);
            }
        }
    });
}

function selectTeacher(period, teacher) {
    let dropdown = document.getElementById(`teacher-dropdown-${period}`);
    dropdown.style.display = "none";

    let notif = document.getElementById(`teacher-notif-${period}`);
    let notifText = document.getElementById(`teacher-notif-text-${period}`);

    notifText.innerHTML = teacher;
    notif.style.display = "block";

    let form = document.getElementById('form-invis');

    let input = form.querySelector(`#input-invis-${period}`);

    if (input.id.endsWith(period)) {
        input.setAttribute('value', teacher);
    }
    if (originalMargin !== 0) {
        $(document.getElementById(`dropdown-container-${period}`)).css('margin-top', originalMargin);
        $(document.getElementById(`dropdown-container-${period}`)).css('margin-bottom', originalMargin);
    } else {
        originalMargin = 45;
        $(document.getElementById(`dropdown-container-${period}`)).css('margin-top', originalMargin);
        $(document.getElementById(`dropdown-container-${period}`)).css('margin-bottom', originalMargin);
    }
}

function unselectTeacher(period) {
    let notif = document.getElementById(`teacher-notif-${period}`);
    let notifText = document.getElementById(`teacher-notif-text-${period}`);

    notifText.innerHTML = "";
    notif.style.display = "none";

    let dropdown = document.getElementById(`teacher-dropdown-${period}`);
    dropdown.style.display = "block";

    $('#form').css('margin-bottom', 100);

    document.getElementById(`input-invis-${period}`).value = '';

    document.getElementById(`teacherInput${period}`).value = '';
    filterTeachers(period);
}

function setOriginalMargin() {
    originalMargin = parseInt($(document.getElementsByClassName('teacher-dropdown')[0]).css('margin-bottom').replace("px", ""));
}
