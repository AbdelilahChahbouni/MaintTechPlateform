/**
 * Main application client script for MaintTech Jobs Maroc
 */

document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------------
    // 1. Mobile Navigation Toggle
    // -----------------------------------------------------------------
    const mobileMenuBtn = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // -----------------------------------------------------------------
    // 2. Flash Messages Dismissal
    // -----------------------------------------------------------------
    const alertCloseBtns = document.querySelectorAll('.alert-close-btn');
    alertCloseBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const alertBox = e.target.closest('.alert-box');
            if (alertBox) {
                alertBox.style.opacity = '0';
                setTimeout(() => alertBox.remove(), 250);
            }
        });
    });

    // Auto-dismiss info alerts after 6 seconds
    setTimeout(() => {
        document.querySelectorAll('.auto-dismiss').forEach(el => {
            el.style.transition = 'opacity 0.4s ease';
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 400);
        });
    }, 6000);

    // -----------------------------------------------------------------
    // 3. Interactive Skill Tag Picker for Dashboard
    // -----------------------------------------------------------------
    const tagButtons = document.querySelectorAll('.skill-tag-btn');
    tagButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const checkbox = btn.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                if (checkbox.checked) {
                    btn.classList.add('bg-blue-600', 'text-white', 'border-blue-600');
                    btn.classList.remove('bg-slate-100', 'text-slate-700', 'border-slate-200');
                } else {
                    btn.classList.remove('bg-blue-600', 'text-white', 'border-blue-600');
                    btn.classList.add('bg-slate-100', 'text-slate-700', 'border-slate-200');
                }
            }
        });
    });
});
