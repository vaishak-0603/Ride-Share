// Admin Panel JavaScript Utilities

// Confirm before destructive actions
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

// Show loading overlay
function showLoading() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.id = 'loadingOverlay';
    overlay.innerHTML = `
        <div class="spinner-border text-light" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(overlay);
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : (type === 'danger' ? 'exclamation-triangle' : 'info-circle')}-fill me-2"></i>
        ${message}
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert:not(.alert-light)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

// Table search functionality
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const tr = table.getElementsByTagName('tr');

    input.addEventListener('keyup', function () {
        const filter = this.value.toLowerCase();

        for (let i = 1; i < tr.length; i++) {
            const td = tr[i].getElementsByTagName('td');
            let found = false;

            for (let j = 0; j < td.length; j++) {
                if (td[j].textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }

            tr[i].style.display = found ? '' : 'none';
        }
    });
}
