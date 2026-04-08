/* ── UpTrail — base.js ───────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss flash messages after 4 seconds
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      el.style.opacity = '0';
      el.style.transform = 'translateX(30px)';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });

  // Profile dropdown toggle
  const profile = document.querySelector('.nav-profile');
  const avatar = document.querySelector('.nav-avatar');
  const dropdown = document.querySelector('.nav-profile-dropdown');

  if (profile && avatar && dropdown) {
    avatar.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (!profile.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  }
});
