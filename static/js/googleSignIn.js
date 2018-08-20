function signOut(onDone) {
    gapi.load('auth2', () => {
        gapi.auth2.init({client_id: '764760025104-is3262o216isl5tbfj4aakcel2tirl7n.apps.googleusercontent.com'}).then(() => {
            gapi.auth2.getAuthInstance().signOut().then(onDone);
        }, console.error);
    });
}

function onSignIn(user) {
    if (!user.getBasicProfile().getEmail().endsWith('k12.andoverma.us')) {
        signOut(() => {
            let errorElement = document.getElementById("login-error");
            if(!errorElement){
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

            errorElement.innerHTML = "You need to sign in with a <strong>k12.andoverma.us</strong> account!"
        });
        return;
    }

    $('#token').val(user.getAuthResponse().id_token);
    document.forms[0].submit();
}