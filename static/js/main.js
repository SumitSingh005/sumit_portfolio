/* ==========================================================================
   Dribbble Luxury Portfolio - Interactive JavaScript Engine
   3D Tilt & Specular Lighting, Multi-phrase Typewriter & Theme Persistence
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // 2. Theme Management (Dark / Light)
    const savedTheme = localStorage.getItem('portfolio-theme');
    const themeToggle = document.getElementById('theme-toggle');
    const themeLabel = document.getElementById('theme-label');

    function applyTheme(theme) {
        const isLight = theme === 'light';
        document.body.classList.toggle('light-mode', isLight);

        if (themeToggle) {
            themeToggle.setAttribute('aria-pressed', String(isLight));
        }

        if (themeLabel) {
            themeLabel.textContent = isLight ? 'Light' : 'Dark';
        }
    }

    // Default to sleek dark mode
    applyTheme(savedTheme || 'dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.body.classList.contains('light-mode') ? 'light' : 'dark';
            const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
            localStorage.setItem('portfolio-theme', nextTheme);
            applyTheme(nextTheme);
        });
    }

    // 3. Multi-phrase Typewriter Animation
    const phrases = [
        'AI & Neural Systems Builder',
        'Django Backend Architect',
        'Full Stack Product Engineer',
        'Machine Learning Practitioner'
    ];
    
    let phraseIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typingElement = document.getElementById('typing');

    function typeLoop() {
        if (!typingElement) return;

        const currentPhrase = phrases[phraseIndex];

        if (isDeleting) {
            typingElement.textContent = currentPhrase.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typingElement.textContent = currentPhrase.substring(0, charIndex + 1);
            charIndex++;
        }

        let typeSpeed = isDeleting ? 40 : 80;

        if (!isDeleting && charIndex === currentPhrase.length) {
            typeSpeed = 2200; // Pause at end of phrase
            isDeleting = true;
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            phraseIndex = (phraseIndex + 1) % phrases.length;
            typeSpeed = 400; // Brief pause before starting next phrase
        }

        setTimeout(typeLoop, typeSpeed);
    }

    typeLoop();

    // 4. Interactive 3D Tilt Effect on Glass Cards
    const tiltCards = document.querySelectorAll('.project-card-3d, .glass-showcase-card, .bento-card');

    tiltCards.forEach((card) => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * -7;
            const rotateY = ((x - centerX) / centerX) * 7;

            card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    // 5. Scroll Reveal with Intersection Observer
    const revealElements = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -40px 0px'
        });

        revealElements.forEach((el) => {
            revealObserver.observe(el);
        });
    } else {
        revealElements.forEach((el) => {
            el.classList.add('is-visible');
        });
    }
});
