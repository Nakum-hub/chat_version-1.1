export {};

function initNav() {
  const headerNode = document.getElementById('header');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const navMenu = document.getElementById('nav-menu');
  const mobileMenuCloseBtn = document.getElementById('mobile-menu-close');
  const backToTop = document.getElementById('back-to-top');
  if (!headerNode || headerNode.dataset.navInit === '1') return;
  const header: HTMLElement = headerNode;
  header.dataset.navInit = '1';

  let lastScroll = 0;
  const mobileBreakpoint = window.matchMedia('(max-width: 1100px)');

  function syncMenuIcon(isOpen: boolean) {
    const icon = mobileMenuBtn?.querySelector('i');
    if (!icon) return;

    if (!mobileBreakpoint.matches) {
      icon.classList.add('fa-bars');
      icon.classList.remove('fa-xmark');
      mobileMenuBtn?.setAttribute('aria-expanded', 'false');
      return;
    }

    icon.classList.toggle('fa-bars', !isOpen);
    icon.classList.toggle('fa-xmark', isOpen);
    mobileMenuBtn?.setAttribute('aria-expanded', String(isOpen));
  }

  function closeMobileMenu() {
    navMenu?.classList.remove('active');
    document.body.classList.remove('menu-open');
    syncMenuIcon(false);
  }

  function openMobileMenu() {
    navMenu?.classList.add('active');
    document.body.classList.add('menu-open');
    header.classList.remove('hidden');
    syncMenuIcon(true);
  }

  closeMobileMenu();

  // Scroll hide/show + scrolled class logic
  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    if (currentScroll > 50) {
      header?.classList.add('scrolled');
      if (!document.body.classList.contains('menu-open') && currentScroll > lastScroll && currentScroll > 200) {
        header?.classList.add('hidden');
      } else {
        header?.classList.remove('hidden');
      }
    } else {
      header?.classList.remove('scrolled', 'hidden');
    }

    // Back to top visibility
    if (backToTop) {
      if (currentScroll > 400) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    }

    lastScroll = currentScroll;
  });

  // Mobile menu toggle
  mobileMenuBtn?.addEventListener('click', (event) => {
    event.preventDefault();

    if (!mobileBreakpoint.matches) {
      closeMobileMenu();
      return;
    }

    const isOpen = navMenu?.classList.contains('active') ?? false;
    if (isOpen) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  });

  mobileMenuCloseBtn?.addEventListener('click', (event) => {
    event.preventDefault();
    closeMobileMenu();
    mobileMenuBtn?.focus();
  });

  // Close mobile menu when clicking a link
  navMenu?.querySelectorAll('.nav-link, .dropdown-item').forEach(link => {
    link.addEventListener('click', () => {
      closeMobileMenu();
    });
  });

  document.addEventListener('click', event => {
    const target = event.target as Node;
    if (!mobileBreakpoint.matches || !navMenu?.classList.contains('active')) return;
    if (navMenu.contains(target) || mobileMenuBtn?.contains(target)) return;
    closeMobileMenu();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && navMenu?.classList.contains('active')) {
      closeMobileMenu();
      mobileMenuBtn?.focus();
    }
  });

  let resizeTimer = 0;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      header.classList.remove('hidden');
      closeMobileMenu();
    }, 100);
  });

  window.addEventListener('pageshow', () => {
    header.classList.remove('hidden');
    closeMobileMenu();
  });
}

document.addEventListener('DOMContentLoaded', initNav);
document.addEventListener('astro:page-load', initNav);
