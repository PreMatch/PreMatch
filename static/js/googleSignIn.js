function signOut(onDone) {
    gapi.load('auth2', () => {
        gapi.auth2.init({client_id: '764760025104-is3262o216isl5tbfj4aakcel2tirl7n.apps.googleusercontent.com'}).then(() => {
            gapi.auth2.getAuthInstance().signOut().then(onDone);
        }, console.error);
    });
}

function signInError(message) {
    signOut(() => {
        let errorElement = document.getElementById("login-error");
        if (!errorElement) {
            let box = document.getElementById("login-box");
            let br = document.createElement("br");
            let p = document.createElement("p");
            p.setAttribute("id", "login-error");
            p.setAttribute("class", "subtitle is-6");
            box.appendChild(br);
            box.appendChild(p);
            sleep(500);
            errorElement = document.getElementById("login-error");
        }

        errorElement.innerHTML = message;
    });
}

function onSignIn(user) {
    let email = user.getBasicProfile().getEmail();
    if (!email.endsWith('k12.andoverma.us')) {
        signInError("You need to sign in with a <strong>k12.andoverma.us</strong> account!");
        return;
    } else {
        let handle = email.split('@')[0];
        let regex = "^.+?\\d$";
        let endsWithNumber = handle.match(regex) !== null;

        if (!endsWithNumber) {
            signInError("You need to be a student to use this site, <em>for now!</em>");
            return;
        }

        let lastNumIndex = handle.length - 4; // Default to 4 digits

        // Find out how many digits (in case of multiple people with same first initial + last name, which would add a fifth)
        for (let i = handle.length - 1; i >= 0; i--) {
            let character = handle[i];
            let isDigit = character.match(/[0-9]/) !== null;

            if (isDigit) {
                lastNumIndex = i;
            } else {
                break;
            }
        }

        let yearOfGraduation = parseInt(handle.slice(lastNumIndex, lastNumIndex + 4));

        let currentDate = new Date();
        let currentMonth = currentDate.getMonth() + 1;
        let currentYear = currentDate.getFullYear();
        let seniorYOG, freshmanYOG;

        // This assumes that summer has always started before August
        if (currentMonth >= 8) {
            // Year before current senior YOG (at the time being written, 2018, when seniors' handles end in 2019)
            // Therefore, we only let people through if their YOG is between year + 1 and year + 4
            seniorYOG = currentYear + 1;
            freshmanYOG = currentYear + 4;
        } else {
            // Year of current senior YOG (at the time being written, 2019, when seniors' handles end in 2019)
            // Therefore, we only let people through if their YOG is between year and year + 3
            seniorYOG = currentYear;
            freshmanYOG = currentYear + 3;
        }

        if (yearOfGraduation >= seniorYOG && yearOfGraduation <= freshmanYOG) {
            // Currently in high school
            $('#token').val(user.getAuthResponse().id_token);
            document.forms[0].submit();
        } else {
            // Currently not in high school
            signInError('Sorry, but you have to <strong>currently be in high school</strong> to use PreMatch!');
        }
    }
}