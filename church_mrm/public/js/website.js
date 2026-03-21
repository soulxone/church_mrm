// Church MRM - Website portal customizations
document.addEventListener('DOMContentLoaded', function () {
    var isLoggedIn = document.cookie.indexOf('user_id=Guest') === -1 &&
                     document.cookie.indexOf('user_id=') !== -1;

    // Frappe renders the user dropdown after DOMContentLoaded,
    // so we poll briefly until the link appears.
    if (isLoggedIn) {
        var attempts = 0;
        var interval = setInterval(function () {
            attempts++;
            var appsLink = document.querySelector('a[href="/apps"]');
            if (appsLink) {
                appsLink.setAttribute('href', '/expense-scanner');
                appsLink.textContent = 'Expense Scanner';
                clearInterval(interval);
            }
            if (attempts > 20) clearInterval(interval);
        }, 100);
    }

    // Hide "Documentation" link for guests (non-logged-in users)
    if (!isLoggedIn) {
        var allLinks = document.querySelectorAll('.navbar .dropdown-item');
        allLinks.forEach(function (link) {
            if (link.getAttribute('href') === '/church-apps') {
                link.style.display = 'none';
            }
        });
    }
});
