// Disable HTML5 validation for better UX
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.setAttribute('novalidate', 'novalidate');
    });
});