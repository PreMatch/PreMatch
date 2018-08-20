function buildForm(periods, teachers) {
    let form = document.getElementById('form');

    periods.forEach((period) => {
        let div = document.createElement('div');
        div.setAttribute("class", "teacher-dropdown");

        let contentDiv = document.createElement('div');
        contentDiv.setAttribute("class", "teacher-dropdown-content");
        contentDiv.setAttribute('id', `teacher-dropdown${period}`)

        let textBox = document.createElement('input');
        textBox.setAttribute("type", "text");
        textBox.setAttribute("placeholder", "Search for a teacher...");
        textBox.setAttribute("id", `teacherInput${period}`);
        textBox.setAttribute("onkeyup", `filterTeachers("${period})"`);

        let labelElement = document.createElement('label');
        labelElement.setAttribute("for", `teacherInput${period}`);
        labelElement.innerHTML = `Block ${period}: `;

        form.appendChild(div);
        div.appendChild(contentDiv);
        contentDiv.appendChild(labelElement);
        contentDiv.appendChild(textBox);

        for (let i = 0; i < teachers.length; i++) {
            let teacher = teachers[i];
            let a = document.createElement('a');
            a.innerHTML = teacher;
            contentDiv.appendChild(a);
        }
    });

    let submit = document.createElement('input');
    submit.setAttribute("type", "submit");
    form.appendChild(submit);
}

function filterTeachers(period) {
    let input, filter, a, i;
    input = document.getElementById(`teacherInput${period}`);
    filter = input.value.toUpperCase();
    let div = document.getElementById(`teacher-dropdown${period}`);
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
        } else {
            a[i].style.display = "none";
        }
    }
}
