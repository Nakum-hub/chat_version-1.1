const activeAnimations = new WeakMap<HTMLElement, number>();
let counterObserver: IntersectionObserver | null = null;
const COUNTER_LOCK_KEY = 'cyberfyx-counters-complete';

const STORAGE_KEY = 'cyberfyx_counters_animated';
let isPageReload = false;

export function initCounters() {
  const counters = Array.from(document.querySelectorAll<HTMLElement>('.counter'));

  if (counterObserver) {
    counterObserver.disconnect();
    counterObserver = null;
  }

  if (!counters.length) return;

  // If this is a page reload, reset the animation flag so counters animate again
  if (isPageReload) {
    sessionStorage.removeItem(STORAGE_KEY);
    isPageReload = false;
  }

  const hasAnimatedBefore = sessionStorage.getItem(STORAGE_KEY) === 'true';
  counters.forEach(counter => prepareCounter(counter, hasAnimatedBefore));

  if (!('IntersectionObserver' in window)) {
    counters.forEach(counter => animateWhenNeeded(counter));
    return;
  }

  counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;

      const counter = entry.target as HTMLElement;
      animateWhenNeeded(counter);

      if (counter.getAttribute('data-animated') === 'true') {
        counterObserver?.unobserve(counter);
      }
    });
  }, {
    threshold: 0.45,
    rootMargin: '0px 0px -24px 0px',
  });

  counters.forEach(counter => counterObserver?.observe(counter));
}

function prepareCounter(counter: HTMLElement, hasAnimatedBefore: boolean) {
  const target = parseInt(counter.getAttribute('data-target') || '0', 10);
  const isCounterLocked = window.sessionStorage.getItem(COUNTER_LOCK_KEY) === 'true';
  if (isCounterLocked) {
    stopCounterAnimation(counter);
    counter.textContent = target.toString();
    counter.setAttribute('data-animated', 'true');
    return;
  }

  const renderedValue = parseInt(counter.textContent || '0', 10);
  const isAlreadyComplete = counter.getAttribute('data-animated') === 'true' && renderedValue === target;

  // If counters were already animated before, restore the target value and mark as animated
  if (hasAnimatedBefore) {
    counter.textContent = target.toString();
    counter.setAttribute('data-animated', 'true');
    return;
  }

  if (isAlreadyComplete) {
    counter.textContent = target.toString();
    return;
  }

  stopCounterAnimation(counter);
  counter.textContent = '0';
  counter.setAttribute('data-animated', 'false');
}

function animateWhenNeeded(counter: HTMLElement) {
  if (counter.getAttribute('data-animated') === 'true') return;

  const target = parseInt(counter.getAttribute('data-target') || '0', 10);
  animateCounter(counter, target);
  counter.setAttribute('data-animated', 'true');
  window.sessionStorage.setItem(COUNTER_LOCK_KEY, 'true');
}

function stopCounterAnimation(counter: HTMLElement) {
  const frameId = activeAnimations.get(counter);
  if (typeof frameId === 'number') {
    window.cancelAnimationFrame(frameId);
    activeAnimations.delete(counter);
  }
}

function animateCounter(element: HTMLElement, target: number) {
  stopCounterAnimation(element);

  const duration = 2000;
  const startTime = performance.now();

  const animate = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const easeProgress = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(target * easeProgress);

    element.textContent = current.toString();

    if (progress < 1) {
      const frameId = window.requestAnimationFrame(animate);
      activeAnimations.set(element, frameId);
      return;
    }

    element.textContent = target.toString();
    activeAnimations.delete(element);
    
    // Mark counters as animated in session storage so they don't animate again
    sessionStorage.setItem(STORAGE_KEY, 'true');
  };

  const frameId = window.requestAnimationFrame(animate);
  activeAnimations.set(element, frameId);
}

// Mark as page reload on DOMContentLoaded (full page load or hard refresh)
document.addEventListener('DOMContentLoaded', () => {
  isPageReload = true;
  initCounters();
});

// On astro navigation (soft page load), only initialize counters
document.addEventListener('astro:page-load', initCounters);

window.addEventListener('pageshow', () => {
  isPageReload = true;
  initCounters();
});
