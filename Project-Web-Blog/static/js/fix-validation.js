// COMPLETE VALIDATION FIX SCRIPT
document.addEventListener('DOMContentLoaded', function() {
    console.log('Applying validation fixes...');
    
    // 1. Remove all maxlength attributes
    document.querySelectorAll('input, textarea').forEach(element => {
        element.removeAttribute('maxlength');
        element.removeAttribute('minlength');
        element.removeAttribute('pattern');
        element.removeAttribute('max');
        element.removeAttribute('min');
    });
    
    // 2. Disable HTML5 validation on all forms
    document.querySelectorAll('form').forEach(form => {
        form.setAttribute('novalidate', 'novalidate');
        
        // Remove any hidden validation inputs
        const hiddenInputs = form.querySelectorAll('input[type="hidden"]');
        hiddenInputs.forEach(input => {
            if (input.name.includes('csrf') || input.name.includes('maxlength')) {
                input.remove();
            }
        });
    });
    
    // 3. Fix for WTForms generated inputs
    document.querySelectorAll('[data-maxlength]').forEach(element => {
        element.removeAttribute('data-maxlength');
    });
    
    console.log('Validation fixes applied successfully!');
});

// Also run on page changes (for SPA-like behavior)
if (window.MutationObserver) {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.tagName === 'FORM' || node.querySelector('form')) {
                            document.querySelectorAll('form').forEach(form => {
                                form.setAttribute('novalidate', 'novalidate');
                            });
                            document.querySelectorAll('input, textarea').forEach(element => {
                                element.removeAttribute('maxlength');
                            });
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}