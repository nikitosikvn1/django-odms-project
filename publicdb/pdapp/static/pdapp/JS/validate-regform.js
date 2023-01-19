function isValidEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function isValidUsername(username) {
    const re = /^[a-zA-Z0-9]+$/;
    return re.test(username);
}

function isValidPassword(password1, password2) {
    return password1 === password2 && password1.length >= 8;
}

const form = document.querySelector('#formId');
form.addEventListener('submit', () => {
    const email = document.querySelector("#email").value;
    const username = document.querySelector("#username").value;
    const password1 = document.querySelector("#password1").value;
    const password2 = document.querySelector("#password2").value;
    const errorMessage = document.querySelector("#error-message");

    let isValid = true;

    if (!isValidEmail(email)) {
        errorMessage.innerHTML = "Please enter a valid email address.";
        isValid = false;
    }

    if (!isValidUsername(username)) {
        errorMessage.innerHTML = "Please enter a valid username.";
        isValid = false;
    }

    if (!isValidPassword(password1, password2)) {
        errorMessage.innerHTML = "Passwords do not match or are less than 8 characters.";
        isValid = false;
    }

    if (!isValid) {
        e.preventDefault();
    }
});

