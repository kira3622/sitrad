/**
 * Material Dashboard Django - Interactive Components
 * Modern Material Design JavaScript functionality
 */

class MaterialDashboard {
    constructor() {
        this.init();
    }

    init() {
        this.initRippleEffect();
        this.initDrawer();
        this.initSnackbar();
        this.initFAB();
        this.initCards();
        this.initTables();
        this.initForms();
        this.initThemeToggle();
        this.initProgressBars();
        this.initTooltips();
    }

    // Material Ripple Effect
    initRippleEffect() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('.material-btn, .material-card, .material-drawer-item');
            if (!button) return;

            const ripple = document.createElement('span');
            const rect = button.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('material-ripple');

            button.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });

        // Add ripple CSS
        const style = document.createElement('style');
        style.textContent = `
            .material-ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            }
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // Navigation Drawer
    initDrawer() {
        const drawerToggle = document.querySelector('.drawer-toggle');
        const drawer = document.querySelector('.material-drawer');
        const overlay = document.createElement('div');
        
        overlay.className = 'material-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 998;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(overlay);

        if (drawerToggle && drawer) {
            drawerToggle.addEventListener('click', () => {
                drawer.classList.toggle('open');
                if (drawer.classList.contains('open')) {
                    overlay.style.opacity = '1';
                    overlay.style.visibility = 'visible';
                } else {
                    overlay.style.opacity = '0';
                    overlay.style.visibility = 'hidden';
                }
            });

            overlay.addEventListener('click', () => {
                drawer.classList.remove('open');
                overlay.style.opacity = '0';
                overlay.style.visibility = 'hidden';
            });
        }
    }

    // Snackbar Notifications
    initSnackbar() {
        window.showSnackbar = (message, duration = 3000) => {
            const snackbar = document.createElement('div');
            snackbar.className = 'material-snackbar';
            snackbar.textContent = message;
            document.body.appendChild(snackbar);

            setTimeout(() => snackbar.classList.add('show'), 100);
            setTimeout(() => {
                snackbar.classList.remove('show');
                setTimeout(() => snackbar.remove(), 300);
            }, duration);
        };

        // Show snackbar for Django messages
        const messages = document.querySelectorAll('.messages .alert');
        messages.forEach(message => {
            const text = message.textContent.trim();
            if (text) {
                showSnackbar(text);
                message.style.display = 'none';
            }
        });
    }

    // Floating Action Button
    initFAB() {
        const fab = document.querySelector('.material-fab');
        if (fab) {
            let lastScrollTop = 0;
            window.addEventListener('scroll', () => {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    fab.style.transform = 'scale(0)';
                } else {
                    fab.style.transform = 'scale(1)';
                }
                lastScrollTop = scrollTop;
            });
        }
    }

    // Enhanced Cards
    initCards() {
        const cards = document.querySelectorAll('.material-card');
        cards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
            });
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });

        // Animate cards on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('material-fade-in');
                }
            });
        }, observerOptions);

        cards.forEach(card => observer.observe(card));
    }

    // Enhanced Tables
    initTables() {
        const tables = document.querySelectorAll('.material-table');
        tables.forEach(table => {
            // Add sorting functionality
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(table, header);
                });
            });

            // Add row selection
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                row.addEventListener('click', () => {
                    rows.forEach(r => r.classList.remove('selected'));
                    row.classList.add('selected');
                });
            });
        });
    }

    sortTable(table, header) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const index = Array.from(header.parentNode.children).indexOf(header);
        const isAscending = header.classList.contains('sort-asc');

        rows.sort((a, b) => {
            const aText = a.children[index].textContent.trim();
            const bText = b.children[index].textContent.trim();
            
            if (isAscending) {
                return bText.localeCompare(aText);
            } else {
                return aText.localeCompare(bText);
            }
        });

        // Update header classes
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        header.classList.add(isAscending ? 'sort-desc' : 'sort-asc');

        // Reorder rows
        rows.forEach(row => tbody.appendChild(row));
    }

    // Enhanced Forms
    initForms() {
        const inputs = document.querySelectorAll('.material-input input, .material-input select, .material-input textarea');
        inputs.forEach(input => {
            // Auto-resize textareas
            if (input.tagName === 'TEXTAREA') {
                input.addEventListener('input', () => {
                    input.style.height = 'auto';
                    input.style.height = input.scrollHeight + 'px';
                });
            }

            // Validation feedback
            input.addEventListener('blur', () => {
                this.validateField(input);
            });
        });

        // Form submission with loading state
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<i class="material-icons">hourglass_empty</i> Chargement...';
                }
            });
        });
    }

    validateField(field) {
        const container = field.closest('.material-input');
        const errorMsg = container.querySelector('.error-message');
        
        if (errorMsg) errorMsg.remove();

        if (field.hasAttribute('required') && !field.value.trim()) {
            this.showFieldError(container, 'Ce champ est requis');
            return false;
        }

        if (field.type === 'email' && field.value && !this.isValidEmail(field.value)) {
            this.showFieldError(container, 'Adresse email invalide');
            return false;
        }

        container.classList.remove('error');
        return true;
    }

    showFieldError(container, message) {
        container.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: var(--md-error);
            font-size: 0.75rem;
            margin-top: 4px;
        `;
        container.appendChild(errorDiv);
    }

    isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // Theme Toggle
    initThemeToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                document.body.classList.toggle('dark-theme');
                localStorage.setItem('darkTheme', document.body.classList.contains('dark-theme'));
            });

            // Load saved theme
            if (localStorage.getItem('darkTheme') === 'true') {
                document.body.classList.add('dark-theme');
            }
        }
    }

    // Progress Bars
    initProgressBars() {
        const progressBars = document.querySelectorAll('.material-progress-bar');
        progressBars.forEach(bar => {
            const targetWidth = bar.dataset.progress || '0';
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
            }, 100);
        });
    }

    // Tooltips
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'material-tooltip';
        tooltip.textContent = text;
        tooltip.style.cssText = `
            position: absolute;
            background: #323232;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            z-index: 1002;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        setTimeout(() => tooltip.style.opacity = '1', 10);
        
        this.currentTooltip = tooltip;
    }

    hideTooltip() {
        if (this.currentTooltip) {
            this.currentTooltip.style.opacity = '0';
            setTimeout(() => {
                if (this.currentTooltip) {
                    this.currentTooltip.remove();
                    this.currentTooltip = null;
                }
            }, 300);
        }
    }

    // Utility Methods
    static showLoader() {
        const loader = document.createElement('div');
        loader.className = 'material-loader';
        loader.innerHTML = `
            <div class="material-spinner">
                <svg viewBox="0 0 50 50">
                    <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                        <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                        <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                    </svg>
                </div>
        `;
        loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255,255,255,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1003;
        `;
        document.body.appendChild(loader);
        return loader;
    }

    static hideLoader(loader) {
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => loader.remove(), 300);
        }
    }
}

// Initialize Material Dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MaterialDashboard();
});

// Export for use in other scripts
window.MaterialDashboard = MaterialDashboard;