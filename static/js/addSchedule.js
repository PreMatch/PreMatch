let originalMargin = 0;
let teachers;

function submitChanges(periods, semesters, lunchPeriods, lunchNumbers) {
    // Remove empty lunch inputs
    $('.lunch-input').each((_, elem) => {
        if (elem.value === '') {
            $(elem).remove();
        }
    });

    let valid = true;
    periods.forEach((period) => {
        semesters.forEach((semester) => {
            let form = document.getElementById('form-invis');

            let input = form.querySelector(`#input-invis-${period}-${semester}`);
            let value = input.value;
            if (!(value.length > 0)) {
                valid = false;
            } else {
                if (!teachers.includes(value)) {
                    valid = false;
                }
            }
        });
    });

    lunchPeriods.forEach((period) => {
        semesters.forEach((semester) => {
            let lunch = document.getElementById(`lunch-invis-${period}-${semester}`);

            if (lunch != null) {
                if (lunch.value) {
                    let parsed = parseInt(lunch.value);

                    if (isNaN(parsed))
                        valid = false;
                    else if (!lunchNumbers.includes(parsed))
                        valid = false;
                }
            }
        });
    });

    if (valid) {
        document.getElementById('form-invis').submit();
    } else {
        document.getElementById(
            'err-msg').innerHTML = "Sorry, but your form isn't valid! <br> Make sure <strong>all of your classes have a teacher selected</strong> and that you <strong>didn't</strong> try to edit the site's code to break it."
    }
}

function filterTeachers(period, semester) {
    let input, filter, a, i;
    input = document.getElementById(`teacherInput${period}-${semester}`);
    filter = input.value.toUpperCase();

    let linkHolder = document.getElementById(`link-holder-${period}-${semester}`);

    let noResultsText = document.getElementById(`no-results-${period}-${semester}`);
    noResultsText.style.display = "none";

    if (filter.length > 0) {
        linkHolder.style.display = "Block";
        let div = document.getElementById(`teacher-dropdown-${period}-${semester}`);
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

        let container = document.getElementById(`dropdown-container-${period}-${semester}`);
        if ($(linkHolder).innerHeight() > 0) {
            $(container).css('margin-bottom', originalMargin + $(linkHolder).innerHeight());
        }

    } else {
        linkHolder.style.display = "None";
        $(document.getElementById(`dropdown-container-${period}-${semester}`)).css('margin-bottom', originalMargin);
    }
}

function selectInput(period, semester) {
    let form = document.getElementById('form');
    $(form).children().each((index) => {
        if (form.children[index].tagName === "DIV") {
            let contentDiv = form.children[index].children[0];
            if (typeof contentDiv.getElementsByTagName('div')[0] != 'undefined' && !contentDiv.id.endsWith(period)) {
                contentDiv.getElementsByTagName('div')[0].style.display = "None";
                let container = document.getElementById(`dropdown-container-${contentDiv.id.slice(-1)}-${semester}`);
                $(container).css('margin-bottom', originalMargin);
            }
        }
    });
}

function decodeEscapes(str) {
    return str.replace(/&#(\d+);/g, function (match, dec) {
        return String.fromCharCode(dec);
    });
}

function selectTeacher(period, semester, teacher) {
    let dropdown = document.getElementById(`teacher-dropdown-${period}-${semester}`);
    dropdown.style.display = "none";

    let notif = document.getElementById(`teacher-notif-${period}-${semester}`);

    let button = document.getElementById(`view-roster-${period}-${semester}`);
    if (button !== null) {
        let currentHref = button.getAttribute('data-href-base');
        let newHref = currentHref + decodeEscapes(teacher);
        button.setAttribute('href', newHref);
    }

    let notifText = document.getElementById(`teacher-notif-text-${period}-${semester}`);

    notifText.innerHTML = teacher;
    notif.style.display = "block";

    document.getElementById(`input-invis-${period}-${semester}`).value = teacher;

    let dropdownContainer = document.getElementById(`dropdown-container-${period}-${semester}`);

    if (originalMargin !== 0) {
        $(dropdownContainer).css('margin', `${originalMargin}px 0`);
    } else {
        originalMargin = 45;
        $(dropdownContainer).css('margin', `${originalMargin}px 0`);
    }

    getLunchData(teacher, semester, period);
}

function getLunchData(teacher, semester, period) {
    if (period === 'A' || period === 'B')
        return;

    $.ajax({
        type: "GET",
        url: window.location.href.split("/")[0] + "/api/lunch/number",
        data: {'teacher': teacher, 'block': period, 'semester': semester},
        async: false
    }).done((data) => manageLunchData(data, semester, period));
}

function manageLunchData(data, semester, period) {
    if (data.status === 'ok' && data.code === 200) {
        let number = data.number;
        if (number >= 1 && number <= 4) {
            selectLunch(period, semester, number);
        }
    }
}

function unselectTeacher(period, semester) {
    let notif = document.getElementById(`teacher-notif-${period}-${semester}`);
    let notifText = document.getElementById(`teacher-notif-text-${period}-${semester}`);

    clearLunch(period, semester);

    notifText.innerHTML = "";
    notif.style.display = "none";

    let dropdown = document.getElementById(`teacher-dropdown-${period}-${semester}`);
    dropdown.style.display = "block";

    $('#form').css('margin-bottom', 100);

    document.getElementById(`input-invis-${period}-${semester}`).value = '';

    document.getElementById(`teacherInput${period}-${semester}`).value = '';
    filterTeachers(period, semester);
}

function openLunchDropdown(period, semester) {
    //Close all other dropdowns
    $('.lunch-options').each((indx, btn) => {
        let split = btn.id.split('-');
        let btnPeriod = split[split.length - 1];
        if (btnPeriod !== period) {
            closeLunchDropdown(btnPeriod);
        }
    });

    let optionsContainer = $(`#lunch-options-${period}-${semester}`);
    $(`#lunch-opener-${period}-${semester}`).css('display', 'none');
    optionsContainer.children('a').each((indx, lunch) => {
        $(lunch).show();
    });
}

function closeLunchDropdown(period, semester) {
    let optionsContainer = $(`#lunch-options-${period}-${semester}`);
    $(`#lunch-opener-${period}-${semester}`).css('display', 'inline-flex');
    optionsContainer.children('a').each((indx, lunch) => {
        $(lunch).hide();
    });
}

function selectLunch(period, semester, lunch) {
    if (document.getElementById(`lunch-invis-${period}-${semester}`)) {
        closeLunchDropdown(period, semester);
        let text = $(`#lunch-select-${period}-${lunch}-${semester}`).html();
        $(`#lunch-opener-${period}-${semester}`).html(text + ' <i class="fas fa-caret-down" style="margin-left: 10px;"></i>');
        document.getElementById(`lunch-invis-${period}-${semester}`).value = lunch;

        const lunchButton = $(`#view-lunch-${period}-${semester}`);
        lunchButton.attr('href', `/lunch/${semester}/${period}/${lunch}`);
        lunchButton.show();
    }

}

function clearLunch(period, semester) {
    if (document.getElementById(`lunch-invis-${period}-${semester}`)) {
        $(`#lunch-opener-${period}-${semester}`).html('Select lunch... <i class="fas fa-caret-down" style="margin-left: 10px;"></i>');
        document.getElementById(`lunch-invis-${period}-${semester}`).value = "";
        $(`#view-lunch-${period}-${semester}`).hide();
    }
}

function setOriginalMargin() {
    originalMargin = parseInt($(document.getElementsByClassName('teacher-dropdown')[0]).css('margin-bottom').replace("px", ""));
}

function togglePublic(checkBox) {
    let checked = checkBox.checked;
    let field = $('#public-input');

    if (checked) {
        field.attr('value', checked);
    } else {
        field.attr('value', '');
    }
}