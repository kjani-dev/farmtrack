// FarmTrack transition system - smooth page navigation + confirmation modals

document.addEventListener('DOMContentLoaded', function() {
    const fadeEl = document.getElementById('page-fade');
    if (!fadeEl) return;

    requestAnimationFrame(function() {
        fadeEl.style.opacity = '1';
    });

    document.querySelectorAll('a[href^="/"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            if (link.target === '_blank' || href.startsWith('//')) return;
            if (href.startsWith('/delete/')) return;
            e.preventDefault();
            fadeEl.classList.add('fade-out');
            setTimeout(function() {
                window.location.href = href;
            }, 350);
        });
    });
});

// Big centered confirmation card - type: 'save', 'edit', or 'delete'
function showConfirmCard(type, title, redirectUrl, delay) {
    const icons = { save: '✓', edit: '✏️', delete: '🗑️' };
    const iconClass = { save: 'icon-save', edit: 'icon-edit', delete: 'icon-delete' };

    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    overlay.innerHTML =
        '<div class="confirm-card">' +
        '<div class="confirm-icon ' + iconClass[type] + '">' + icons[type] + '</div>' +
        '<div class="confirm-title">' + title + '</div>' +
        '</div>';
    document.body.appendChild(overlay);

    requestAnimationFrame(function() {
        overlay.classList.add('show');
    });

    setTimeout(function() {
        if (redirectUrl) window.location.href = redirectUrl;
    }, delay || 900);
}

// Custom delete confirmation dialog - replaces native browser confirm()
function confirmDelete(event, link) {
    event.preventDefault();
    event.stopPropagation();
    const href = link.getAttribute('href');

    const overlay = document.createElement('div');
    overlay.className = 'confirm-overlay';
    overlay.innerHTML =
        '<div class="confirm-card">' +
        '<div class="confirm-icon icon-delete">🗑️</div>' +
        '<div class="confirm-title">Delete this entry?</div>' +
        '<div class="confirm-actions">' +
        '<button class="confirm-btn btn-cancel" id="cancelDeleteBtn">Cancel</button>' +
        '<button class="confirm-btn btn-danger" id="confirmDeleteBtn">Delete</button>' +
        '</div></div>';
    document.body.appendChild(overlay);

    requestAnimationFrame(function() {
        overlay.classList.add('show');
    });

    document.getElementById('cancelDeleteBtn').addEventListener('click', function() {
        overlay.remove();
    });

    document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
        overlay.remove();
        showConfirmCard('delete', 'Entry deleted', href, 700);
    });

    return false;
}
