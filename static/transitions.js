// FarmTrack transition system - smooth page navigation + save confirmation

document.addEventListener('DOMContentLoaded', function() {
    const fadeEl = document.getElementById('page-fade');
    if (!fadeEl) return;

    // Fade in on load
    requestAnimationFrame(function() {
        fadeEl.style.opacity = '1';
    });

    // Intercept internal nav links for fade-out transition
    document.querySelectorAll('a[href^="/"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            if (link.target === '_blank' || href.startsWith('//')) return;
            e.preventDefault();
            fadeEl.classList.add('fade-out');
            setTimeout(function() {
                window.location.href = href;
            }, 350);
        });
    });
});

// Call this after a successful save to show confirmation before redirect
function confirmDelete(link) {
    if (!confirm('Delete this entry? This cannot be undone.')) {
        return false;
    }
    const href = link.getAttribute('href');
    showSaveToast('Entry deleted', href, 500);
    return false;
}

function showSaveToast(message, redirectUrl, delay) {
    const toast = document.createElement('div');
    toast.className = 'save-toast';
    toast.textContent = message || 'Entry saved ✓';
    document.body.appendChild(toast);
    requestAnimationFrame(function() {
        toast.classList.add('show');
    });
    setTimeout(function() {
        if (redirectUrl) window.location.href = redirectUrl;
    }, delay || 700);
}
