/* ═══════════════════════════════════════════════════════
   Asian Trade Corporation - Main JavaScript
   ═══════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function() {

    // Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            // On desktop, adjust main content
            if (window.innerWidth > 992) {
                if (sidebar.style.transform === 'translateX(-100%)') {
                    sidebar.style.transform = '';
                    mainContent.style.marginLeft = '';
                } else {
                    sidebar.style.transform = 'translateX(-100%)';
                    mainContent.style.marginLeft = '0';
                }
            }
        });
    }

    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 992) {
            if (sidebar && sidebar.classList.contains('show') &&
                !sidebar.contains(e.target) &&
                !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm delete forms
    const deleteForms = document.querySelectorAll('form[data-confirm]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm(form.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // Format currency inputs on blur
    const currencyInputs = document.querySelectorAll('input[data-currency]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            const val = parseFloat(this.value);
            if (!isNaN(val)) {
                this.value = val.toFixed(2);
            }
        });
    });

    // Print button
    const printBtns = document.querySelectorAll('.btn-print');
    printBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            window.print();
        });
    });
});
