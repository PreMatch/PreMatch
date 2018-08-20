function signOut() {
    const auth2 = gapi.auth2.getAuthInstance();
    return auth2.signOut();
}

function onSignIn(user) {
    if (!user.getBasicProfile().getEmail().endsWith('k12.andoverma.us')) {
        signOut().then(() => alert("You need to sign in with a k12.andoverma.us account!"));
        return;
    }

    $('#token').val(user.getAuthResponse().id_token);
    document.forms[0].submit();
}