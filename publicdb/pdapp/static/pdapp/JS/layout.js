$(document).ready(function() {
    // Dropdown lists
    $('.sub-button').click(function() {
        $(this).next('.sub-menu').slideToggle();
        $(this).find('.dropdown').toggleClass('rotate');
    });

    // Popup events
    const loginPopupBg = document.querySelector('.login-popup-bg');
    const loginPopupForm = document.querySelector('.login-popup-form');
    const popupCloseButton = document.querySelector('.close-block img');
    const popupOpenButtons = document.querySelectorAll('.open-login-form');

    popupOpenButtons.forEach((button) => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            loginPopupBg.classList.add('active');
            loginPopupForm.classList.add('active');
        });
    });

    popupCloseButton.addEventListener('click', () => {
        loginPopupBg.classList.remove('active');
        loginPopupForm.classList.remove('active');
    });

    document.addEventListener('click', (e) => {
        if (e.target === loginPopupBg) {
            loginPopupBg.classList.remove('active');
            loginPopupForm.classList.remove('active');
        }
    });

    // Form submitting
    const emailField = document.querySelector('.email-field');
    const passwordField = document.querySelector('.password-field');
    const submitButton = document.querySelector('#submit');

    loginPopupForm.addEventListener('change', () => {
        emailLength = emailField.value.length;
        passwordLength = passwordField.value.length;

        if (emailLength >= 3 && passwordLength >= 8) {
            submitButton.disabled = false;
        } else {
            submitButton.disabled = true;
        }
    })
});