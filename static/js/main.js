document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
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

    applyTheme(savedTheme || 'dark');

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const nextTheme = document.body.classList.contains('light-mode') ? 'dark' : 'light';
            localStorage.setItem('portfolio-theme', nextTheme);
            applyTheme(nextTheme);
        });
    }

    // Typewriter Animation
    const text = 'AI Developer | Django Developer | Full Stack Developer';
    let index = 0;

    function type() {
        const typing = document.getElementById('typing');
        if (!typing) {
            return;
        }

        typing.textContent = text.slice(0, index);
        index++;

        if (index <= text.length) {
            setTimeout(type, 70);
        }
    }

    type();

    // Scroll Reveal Observer
    const revealItems = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12 }
        );

        revealItems.forEach((item) => {
            observer.observe(item);
        });
    } else {
        revealItems.forEach((item) => {
            item.classList.add('is-visible');
        });
    }
});
