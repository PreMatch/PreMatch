function signOut() {
    let auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        console.log('User signed out.');
    });
}

function onSignIn(user) {
    if (!user.getBasicProfile().getEmail().endsWith('k12.andoverma.us')) {
        signOut().then(() => alert("You need to sign in with a k12.andoverma.us account!"));
        return;
    }
}
