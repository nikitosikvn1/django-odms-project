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

});