// code_portfolio/static/code_portfolio/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Highlight active nav item
    highlightActiveNav();
    
    // Initialize tooltips
    initTooltips();
    
    // Smooth scrolling for anchor links
    initSmoothScroll();
    
    // Form validation
    initFormValidation();
});

/**
 * Highlights the current active navigation item based on the URL
 */
function highlightActiveNav() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    const currentUrl = window.location.pathname;
    
    navLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        
        // Skip external links
        if (linkHref.startsWith('http')) {
            return;
        }
        
        // Check if current URL starts with the link's href (for nested routes)
        if (currentUrl === linkHref || (linkHref !== '/' && currentUrl.startsWith(linkHref))) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

/**
 * Initializes Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Adds smooth scrolling behavior for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            // Skip if it's just "#" or JavaScript links
            if (targetId === '#' || targetId.startsWith('javascript:')) {
                return;
            }
            
            e.preventDefault();
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                // Add offset for fixed header
                const headerOffset = 100;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initializes form validation
 */
function initFormValidation() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(event) {
            if (!contactForm.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            contactForm.classList.add('was-validated');
        });
    }
}

/**
 * Animates skill progress bars
 */
function animateSkillBars() {
    const skillBars = document.querySelectorAll('.skill-progress .progress-bar');
    
    skillBars.forEach(bar => {
        const width = bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-out';
            bar.style.width = width;
        }, 200);
    });
}

// Initialize skill animations when the skills section is in view
document.addEventListener('DOMContentLoaded', function() {
    const skillsSection = document.querySelector('.skills-overview');
    
    if (skillsSection) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateSkillBars();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        
        observer.observe(skillsSection);
    }
});

// Project filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filter-section .btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!this.classList.contains('active')) {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
            }
        });
    });
});