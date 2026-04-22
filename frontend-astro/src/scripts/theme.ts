export {}; // Ensure this is treated as a module

document.addEventListener('DOMContentLoaded', () => {
  const themeToggle = document.getElementById('theme-toggle');
  
  if (!themeToggle) return;
  
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    if (newTheme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('cyberfyx-theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('cyberfyx-theme', 'light');
    }
  });
});
