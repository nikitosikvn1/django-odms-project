$(document).ready(function() {
    // Arrow rotate faq
    $('.faq-collapse a').click(function() {
        $(this).find('.dropdown').toggleClass('rotate');
    });
});