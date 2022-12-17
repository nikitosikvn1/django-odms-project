$(document).ready(function() {
    // Dropdown lists
    $('.sub-button').click(function() {
        $(this).next('.sub-menu').slideToggle();
        $(this).find('.dropdown').toggleClass('rotate');
    });
});