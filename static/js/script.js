/**
 * Elderly & Disabled Helping System - JavaScript
 * Simple accessibility enhancements
 */

document.addEventListener('DOMContentLoaded', function() {

    // Auto-dismiss alerts after 8 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 8000);
    });

    // Confirm password validation on registration
    var registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            var password = document.getElementById('password').value;
            var confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match. Please try again.');
                document.getElementById('confirm_password').focus();
            }
        });
    }

    // Keyboard shortcut: Alt+H for help (home)
    document.addEventListener('keydown', function(e) {
        if (e.altKey && e.key === 'h') {
            window.location.href = '/';
        }
    });

    // Add aria labels to form inputs without labels
    document.querySelectorAll('input[placeholder]').forEach(function(input) {
        if (!input.getAttribute('aria-label') && !input.id) {
            input.setAttribute('aria-label', input.placeholder);
        }
    });

    // Focus first form field on login/register pages
    var firstInput = document.querySelector('form input:not([type="hidden"])');
    if (firstInput && window.location.pathname.match(/\/(login|register)/)) {
        firstInput.focus();
    }

});
