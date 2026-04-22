export {};

function initAnimations() {
  const faders = document.querySelectorAll('.fade-up:not(.visible)');

  if (!('IntersectionObserver' in window)) {
    // Fallback: make everything visible immediately
    faders.forEach(el => el.classList.add('visible'));
    return;
  }

  const appearOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -40px 0px"
  };

  const appearOnScroll = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, appearOptions);

  faders.forEach(fader => {
    appearOnScroll.observe(fader);
  });
}

// Run on initial load
document.addEventListener('DOMContentLoaded', initAnimations);

// Run after every Astro view transition navigation
document.addEventListener('astro:page-load', initAnimations);
