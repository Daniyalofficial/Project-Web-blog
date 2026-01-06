/* main.js - Gztechiz Blog Platform */

// ========== DROPDOWN TOGGLE ==========
document.addEventListener('DOMContentLoaded', function() {
    // Categories dropdown toggle
    const dropdownToggles = document.querySelectorAll('.navbar-dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdownMenu = this.nextElementSibling;
            const icon = this.querySelector('i');
            
            // Close other dropdowns
            document.querySelectorAll('.navbar-dropdown-menu').forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.style.display = 'none';
                    const otherIcon = menu.previousElementSibling.querySelector('i');
                    if (otherIcon) {
                        otherIcon.classList.remove('fa-chevron-up');
                        otherIcon.classList.add('fa-chevron-down');
                    }
                }
            });
            
            // Toggle current dropdown
            if (dropdownMenu.style.display === 'block') {
                dropdownMenu.style.display = 'none';
                icon.classList.remove('fa-chevron-up');
                icon.classList.add('fa-chevron-down');
            } else {
                dropdownMenu.style.display = 'block';
                icon.classList.remove('fa-chevron-down');
                icon.classList.add('fa-chevron-up');
            }
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar-dropdown')) {
            document.querySelectorAll('.navbar-dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
                const icon = menu.previousElementSibling.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                }
            });
        }
    });
    
    // Prevent dropdown from closing when clicking inside
    document.querySelectorAll('.navbar-dropdown-menu').forEach(menu => {
        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
});

// ========== MOBILE MENU ==========
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
    
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.add('open');
            if (mobileMenuOverlay) mobileMenuOverlay.classList.add('open');
            document.body.style.overflow = 'hidden';
        });
    }
    
    if (mobileMenuClose) {
        mobileMenuClose.addEventListener('click', function() {
            mobileMenu.classList.remove('open');
            if (mobileMenuOverlay) mobileMenuOverlay.classList.remove('open');
            document.body.style.overflow = '';
        });
    }
    
    if (mobileMenuOverlay) {
        mobileMenuOverlay.addEventListener('click', function() {
            mobileMenu.classList.remove('open');
            this.classList.remove('open');
            document.body.style.overflow = '';
        });
    }
});

// ========== COMMENT REPLY FUNCTION ==========
// Reply to comment function
function replyToComment(commentId, authorName) {
    console.log('Replying to:', commentId, authorName);
    
    // Escape special characters in authorName
    const safeAuthorName = authorName
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"');
    
    // Set parent comment ID
    document.getElementById('parent_id').value = commentId;
    
    // Focus and add mention
    const textarea = document.getElementById('text');
    if (textarea) {
        textarea.value = `@${safeAuthorName} `;
        textarea.focus();
        textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Update form title
    const formTitle = document.querySelector('.comment-form h3');
    if (formTitle) {
        formTitle.textContent = `Replying to ${safeAuthorName}`;
        formTitle.style.color = '#3b82f6';
    }
}

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Reply buttons
    document.querySelectorAll('.comment-reply').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const authorName = this.getAttribute('data-author-name');
            replyToComment(commentId, authorName);
        });
    });
});

// ========== THEME TOGGLE ==========
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.querySelector('.theme-toggle');
    const html = document.documentElement;
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            const icon = this.querySelector('i');
            if (icon) {
                icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            html.setAttribute('data-theme', savedTheme);
            const icon = themeToggle.querySelector('i');
            if (icon) {
                icon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            }
        }
    }
});

// ========== FLASH MESSAGES ==========
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(flash => {
        const closeBtn = flash.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-10px)';
                setTimeout(() => flash.remove(), 300);
            });
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (flash.parentNode) {
                flash.style.opacity = '0';
                flash.style.transform = 'translateY(-10px)';
                setTimeout(() => flash.remove(), 300);
            }
        }, 5000);
    });
});

// ========== SEARCH FUNCTIONALITY ==========
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('.navbar-search-input');
    const searchForm = document.querySelector('.search-form');
    
    if (searchInput && searchForm) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    performLiveSearch(query);
                }
            }, 300);
        });
        
        searchForm.addEventListener('submit', function(e) {
            const query = searchInput.value.trim();
            if (!query || query.length < 2) {
                e.preventDefault();
                alert('Please enter at least 2 characters to search');
            }
        });
    }
});

async function performLiveSearch(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        // Implement live search dropdown here if needed
        console.log('Search results:', results);
    } catch (error) {
        console.error('Search error:', error);
    }
}

// ========== SCROLL TO TOP ==========
document.addEventListener('DOMContentLoaded', function() {
    const scrollToTopBtn = document.querySelector('.scroll-to-top');
    
    if (scrollToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.classList.add('visible');
            } else {
                scrollToTopBtn.classList.remove('visible');
            }
        });
        
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

// ========== FORM VALIDATION ==========
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = '#ef4444';
            isValid = false;
        } else {
            input.style.borderColor = '';
        }
    });
    
    return isValid;
}

// ========== IMAGE PREVIEW ==========
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;
    
    preview.innerHTML = '';
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.maxWidth = '200px';
            img.style.maxHeight = '150px';
            img.style.borderRadius = '8px';
            img.style.marginTop = '10px';
            preview.appendChild(img);
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// ========== COPY TO CLIPBOARD ==========
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Link copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showToast('Failed to copy link', 'error');
    }
}

// ========== TOAST NOTIFICATION ==========
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info'}-circle"></i>
        <span>${message}</span>
        <button class="toast-close"><i class="fas fa-times"></i></button>
    `;
    
    document.body.appendChild(toast);
    
    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => toast.remove());
    
    // Auto remove
    setTimeout(() => {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-10px)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 5000);
}

// ========== INITIALIZE EVERYTHING ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('Gztechiz Blog Platform initialized');
});
// ========== LIVE SEARCH SUGGESTIONS ==========
function initLiveSearch() {
    const searchInput = document.querySelector('.navbar-search-input');
    const searchForm = document.querySelector('.navbar-search-form');
    
    if (!searchInput || !searchForm) return;
    
    let searchTimeout;
    let suggestionsContainer = null;
    
    // Create suggestions container
    function createSuggestionsContainer() {
        if (suggestionsContainer) return suggestionsContainer;
        
        suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        suggestionsContainer.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-xl);
            margin-top: 8px;
            z-index: 1000;
            display: none;
            max-height: 400px;
            overflow-y: auto;
        `;
        
        searchForm.parentElement.style.position = 'relative';
        searchForm.parentElement.appendChild(suggestionsContainer);
        return suggestionsContainer;
    }
    
    // Show suggestions
    function showSuggestions(suggestions) {
        const container = createSuggestionsContainer();
        
        if (!suggestions || suggestions.length === 0) {
            container.style.display = 'none';
            return;
        }
        
        container.innerHTML = '';
        
        suggestions.forEach(item => {
            const suggestion = document.createElement('a');
            suggestion.href = `/post/${item.slug}`;
            suggestion.className = 'search-suggestion-item';
            suggestion.style.cssText = `
                display: block;
                padding: 12px 16px;
                color: var(--text-secondary);
                text-decoration: none;
                border-bottom: 1px solid var(--border-light);
                transition: all var(--transition-fast);
            `;
            suggestion.innerHTML = `
                <div style="font-weight: 500; color: var(--text-primary); margin-bottom: 4px;">
                    ${item.title}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-muted);">
                    ${item.excerpt}
                </div>
            `;
            
            suggestion.addEventListener('mouseenter', () => {
                suggestion.style.background = 'var(--bg-secondary)';
            });
            
            suggestion.addEventListener('mouseleave', () => {
                suggestion.style.background = '';
            });
            
            container.appendChild(suggestion);
        });
        
        // Add "View all results" link
        const viewAll = document.createElement('a');
        viewAll.href = `/search?q=${encodeURIComponent(searchInput.value)}`;
        viewAll.className = 'search-suggestion-item';
        viewAll.style.cssText = `
            display: block;
            padding: 12px 16px;
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            text-align: center;
            background: var(--bg-secondary);
        `;
        viewAll.textContent = `View all results for "${searchInput.value}"`;
        container.appendChild(viewAll);
        
        container.style.display = 'block';
    }
    
    // Hide suggestions
    function hideSuggestions() {
        if (suggestionsContainer) {
            setTimeout(() => {
                if (suggestionsContainer) {
                    suggestionsContainer.style.display = 'none';
                }
            }, 200);
        }
    }
    
    // Fetch search suggestions
    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            return results;
        } catch (error) {
            console.error('Search error:', error);
            return [];
        }
    }
    
    // Event Listeners
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        
        const query = this.value.trim();
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        searchTimeout = setTimeout(async () => {
            const suggestions = await fetchSuggestions(query);
            showSuggestions(suggestions);
        }, 300);
    });
    
    searchInput.addEventListener('focus', function() {
        const query = this.value.trim();
        if (query.length >= 2 && suggestionsContainer) {
            suggestionsContainer.style.display = 'block';
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchForm.contains(e.target)) {
            hideSuggestions();
        }
    });
    
    // Form submission
    searchForm.addEventListener('submit', function(e) {
        const query = searchInput.value.trim();
        if (!query || query.length < 2) {
            e.preventDefault();
            searchInput.focus();
            return false;
        }
        return true;
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initLiveSearch);