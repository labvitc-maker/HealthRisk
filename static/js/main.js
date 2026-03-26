// Enhanced notification functions

// Show a toast notification
function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.style.minWidth = '300px';
    toast.innerHTML = `
        <strong><i class="fas fa-bell"></i> Health Alert</strong>
        <p class="mb-0 small">${message}</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    
    // Auto-remove after 8 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 8000);
}

// Check for new notifications on page focus
window.addEventListener('focus', function() {
    updateNotificationCount();
});

// Listen for custom events
document.addEventListener('newNotification', function(e) {
    showNotification(e.detail.message, 'warning');
});