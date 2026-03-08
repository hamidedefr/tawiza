/**
 * TAJINE Advanced Animations
 * Moroccan-inspired interactive animations
 * Version: 1.0.0
 */

(function() {
    'use strict';

    // ═══════════════════════════════════════════════════════════════════
    // SCROLL PROGRESS INDICATOR
    // ═══════════════════════════════════════════════════════════════════

    function createScrollProgress() {
        const progress = document.createElement('div');
        progress.className = 'scroll-progress';
        progress.id = 'scrollProgress';
        document.body.appendChild(progress);

        window.addEventListener('scroll', function() {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPercent = (scrollTop / docHeight) * 100;
            progress.style.width = scrollPercent + '%';
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // FLOATING PARTICLES SYSTEM
    // ═══════════════════════════════════════════════════════════════════

    function createParticles() {
        // Check if container already exists in HTML
        var container = document.querySelector('.particles-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'particles-container';
            container.setAttribute('aria-hidden', 'true');
            document.body.appendChild(container);
        }

        const particleTypes = ['diamond', 'star', 'dot'];
        const particleCount = 20; // Add additional dynamic particles

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            const type = particleTypes[Math.floor(Math.random() * particleTypes.length)];
            particle.className = 'particle particle-' + type + ' dynamic-particle';

            // Random positioning
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 10 + 's';
            particle.style.animationDuration = (15 + Math.random() * 20) + 's';

            container.appendChild(particle);
        }
    }

    // ═══════════════════════════════════════════════════════════════════
    // REVEAL ON SCROLL (Intersection Observer)
    // ═══════════════════════════════════════════════════════════════════

    function initScrollReveal() {
        const revealElements = document.querySelectorAll(
            '.section, .card, .theory-card, .doc-category, .interface-card, ' +
            '.use-case-card, .metric-table, .integration-box, .formula-card'
        );

        revealElements.forEach(function(el) {
            el.classList.add('reveal-element');
        });

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -100px 0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    // Add stagger effect for children
                    const children = entry.target.querySelectorAll('.card, .theory-card');
                    children.forEach(function(child, index) {
                        child.style.transitionDelay = (index * 0.1) + 's';
                    });
                }
            });
        }, observerOptions);

        revealElements.forEach(function(el) {
            observer.observe(el);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // ANIMATED COUNTERS
    // ═══════════════════════════════════════════════════════════════════

    function animateCounters() {
        const counters = document.querySelectorAll('.stat-number, .counter');

        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting && !entry.target.classList.contains('counted')) {
                    entry.target.classList.add('counted');

                    const target = parseInt(entry.target.getAttribute('data-target') ||
                                           entry.target.textContent.replace(/[^0-9]/g, ''));
                    const suffix = entry.target.textContent.replace(/[0-9]/g, '');
                    const duration = 2000;
                    const increment = target / (duration / 16);
                    let current = 0;

                    function updateCounter() {
                        current += increment;
                        if (current < target) {
                            entry.target.textContent = Math.floor(current) + suffix;
                            requestAnimationFrame(updateCounter);
                        } else {
                            entry.target.textContent = target + suffix;
                        }
                    }

                    updateCounter();
                }
            });
        }, { threshold: 0.5 });

        counters.forEach(function(counter) {
            counterObserver.observe(counter);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // 3D TILT EFFECT FOR CARDS
    // ═══════════════════════════════════════════════════════════════════

    function init3DTilt() {
        const cards = document.querySelectorAll('.card, .theory-card, .interface-card');

        cards.forEach(function(card) {
            card.addEventListener('mousemove', function(e) {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;

                card.style.transform =
                    'perspective(1000px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) scale3d(1.02, 1.02, 1.02)';
            });

            card.addEventListener('mouseleave', function() {
                card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // MAGNETIC BUTTONS
    // ═══════════════════════════════════════════════════════════════════

    function initMagneticButtons() {
        const buttons = document.querySelectorAll('.nav-link, .doc-link, .cta-button');

        buttons.forEach(function(btn) {
            btn.addEventListener('mousemove', function(e) {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;

                btn.style.transform = 'translate(' + (x * 0.3) + 'px, ' + (y * 0.3) + 'px)';
            });

            btn.addEventListener('mouseleave', function() {
                btn.style.transform = 'translate(0, 0)';
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // RIPPLE EFFECT ON CLICK
    // ═══════════════════════════════════════════════════════════════════

    function initRippleEffect() {
        document.addEventListener('click', function(e) {
            const target = e.target.closest('.card, .theory-card, .nav-link, .doc-link');
            if (!target) return;

            const ripple = document.createElement('span');
            ripple.className = 'ripple';

            const rect = target.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);

            ripple.style.width = size + 'px';
            ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';

            target.style.position = 'relative';
            target.style.overflow = 'hidden';
            target.appendChild(ripple);

            setTimeout(function() {
                ripple.remove();
            }, 600);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // PARALLAX EFFECT FOR SECTIONS
    // ═══════════════════════════════════════════════════════════════════

    function initParallax() {
        const sections = document.querySelectorAll('.section');

        window.addEventListener('scroll', function() {
            const scrollY = window.scrollY;

            sections.forEach(function(section) {
                const rect = section.getBoundingClientRect();
                const sectionTop = rect.top + scrollY;
                const offset = (scrollY - sectionTop) * 0.1;

                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    const bg = section.querySelector('.section-bg, .zellige-bg');
                    if (bg) {
                        bg.style.transform = 'translateY(' + offset + 'px)';
                    }
                }
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // ZELLIGE BACKGROUND PATTERN GENERATOR
    // ═══════════════════════════════════════════════════════════════════

    function createZelligeBackgrounds() {
        const sections = document.querySelectorAll('.section');

        sections.forEach(function(section, index) {
            const bg = document.createElement('div');
            bg.className = 'zellige-bg zellige-pattern-' + ((index % 3) + 1);
            bg.setAttribute('aria-hidden', 'true');
            section.insertBefore(bg, section.firstChild);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // SMOOTH SCROLL FOR NAVIGATION
    // ═══════════════════════════════════════════════════════════════════

    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const target = document.querySelector(targetId);

                if (target) {
                    const offsetTop = target.offsetTop - 80;
                    window.scrollTo({
                        top: offsetTop,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // TYPING ANIMATION FOR HERO
    // ═══════════════════════════════════════════════════════════════════

    function initTypingEffect() {
        const heroTitle = document.querySelector('.hero-title');
        if (!heroTitle) return;

        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.opacity = '1';

        let i = 0;
        function typeChar() {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeChar, 50);
            }
        }

        setTimeout(typeChar, 500);
    }

    // ═══════════════════════════════════════════════════════════════════
    // GLOWING BORDER ANIMATION FOR ACTIVE SECTION
    // ═══════════════════════════════════════════════════════════════════

    function initActiveSection() {
        const sections = document.querySelectorAll('.section');
        const navLinks = document.querySelectorAll('.nav-link');

        const sectionObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const id = entry.target.getAttribute('id');

                    navLinks.forEach(function(link) {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === '#' + id) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, { threshold: 0.3 });

        sections.forEach(function(section) {
            sectionObserver.observe(section);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // MOUSE TRAILER EFFECT
    // ═══════════════════════════════════════════════════════════════════

    function initMouseTrailer() {
        const trailer = document.createElement('div');
        trailer.className = 'mouse-trailer';
        trailer.setAttribute('aria-hidden', 'true');
        document.body.appendChild(trailer);

        let mouseX = 0, mouseY = 0;
        let trailerX = 0, trailerY = 0;

        document.addEventListener('mousemove', function(e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        function animateTrailer() {
            trailerX += (mouseX - trailerX) * 0.1;
            trailerY += (mouseY - trailerY) * 0.1;

            trailer.style.left = trailerX + 'px';
            trailer.style.top = trailerY + 'px';

            requestAnimationFrame(animateTrailer);
        }

        animateTrailer();

        // Change trailer on interactive elements
        const interactiveElements = document.querySelectorAll('a, button, .card, .theory-card');
        interactiveElements.forEach(function(el) {
            el.addEventListener('mouseenter', function() {
                trailer.classList.add('trailer-active');
            });
            el.addEventListener('mouseleave', function() {
                trailer.classList.remove('trailer-active');
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // LOADING ANIMATION
    // ═══════════════════════════════════════════════════════════════════

    function createLoadingScreen() {
        const loader = document.createElement('div');
        loader.className = 'page-loader';
        loader.id = 'pageLoader';

        const spinner = document.createElement('div');
        spinner.className = 'loader-spinner';

        const text = document.createElement('div');
        text.className = 'loader-text';
        text.textContent = 'TAJINE';

        loader.appendChild(spinner);
        loader.appendChild(text);
        document.body.appendChild(loader);

        window.addEventListener('load', function() {
            setTimeout(function() {
                loader.classList.add('loader-hidden');
                setTimeout(function() {
                    loader.remove();
                }, 500);
            }, 1000);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // STAT CARDS ANIMATION
    // ═══════════════════════════════════════════════════════════════════

    function initStatCards() {
        // Stats are now defined in HTML with data-target attributes
        // This function is kept for backward compatibility but no longer creates elements
        // The animateCounters() function handles the animation
    }

    // ═══════════════════════════════════════════════════════════════════
    // GOLDEN RATIO DIVIDERS
    // ═══════════════════════════════════════════════════════════════════

    function createGoldenDividers() {
        const sections = document.querySelectorAll('.section');

        sections.forEach(function(section, index) {
            if (index === sections.length - 1) return;

            const divider = document.createElement('div');
            divider.className = 'golden-divider';
            divider.setAttribute('aria-hidden', 'true');

            // Create SVG using DOM methods
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('viewBox', '0 0 100 20');
            svg.setAttribute('preserveAspectRatio', 'none');

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', 'M0,10 Q25,0 50,10 Q75,20 100,10');
            path.setAttribute('fill', 'none');
            path.setAttribute('stroke', 'currentColor');
            path.setAttribute('stroke-width', '0.5');

            svg.appendChild(path);
            divider.appendChild(svg);
            section.appendChild(divider);
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // THEORY CARDS FLIP EFFECT
    // ═══════════════════════════════════════════════════════════════════

    function initCardFlip() {
        const theoryCards = document.querySelectorAll('.theory-card');

        theoryCards.forEach(function(card) {
            card.addEventListener('click', function() {
                this.classList.toggle('flipped');
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // GRADIENT ANIMATION FOR BUTTONS
    // ═══════════════════════════════════════════════════════════════════

    function initGradientButtons() {
        const buttons = document.querySelectorAll('.cta-button, .doc-link');

        buttons.forEach(function(btn) {
            btn.addEventListener('mousemove', function(e) {
                const rect = btn.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;

                btn.style.setProperty('--mouse-x', x + '%');
                btn.style.setProperty('--mouse-y', y + '%');
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════
    // INITIALIZATION
    // ═══════════════════════════════════════════════════════════════════

    function init() {
        // Create loading screen first
        createLoadingScreen();

        // Wait for DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initAll);
        } else {
            initAll();
        }
    }

    function initAll() {
        // Create visual elements
        createScrollProgress();
        createParticles();
        createZelligeBackgrounds();
        createGoldenDividers();

        // Initialize interactions
        initScrollReveal();
        animateCounters();
        init3DTilt();
        initMagneticButtons();
        initRippleEffect();
        initParallax();
        initSmoothScroll();
        initActiveSection();
        initMouseTrailer();
        initCardFlip();
        initGradientButtons();

        // Hero specific
        initStatCards();

        // Delay typing effect for dramatic entrance
        setTimeout(initTypingEffect, 1500);

        console.log('TAJINE Animations initialized successfully');
    }

    // Start initialization
    init();

})();
