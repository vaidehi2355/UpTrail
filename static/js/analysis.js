/* ── UpTrail — analysis.js ───────────────────────────────────────────────── */
// COMPLETION_PCT is injected by analysis.html

document.addEventListener('DOMContentLoaded', () => {

  // ── Animate readiness progress bar on load ─────────────────────────────
  const fill = document.querySelector('.prog-fill');
  if (fill) {
    const target = fill.dataset.width || COMPLETION_PCT;
    fill.style.width = '0%';
    requestAnimationFrame(() => {
      setTimeout(() => {
        fill.style.width = target + '%';
      }, 100);
    });
  }

  // ── Animate stat numbers counting up ──────────────────────────────────
  document.querySelectorAll('.stat-num').forEach(el => {
    const raw   = el.textContent.trim();
    const isNum = !raw.includes('%')
      ? parseInt(raw)
      : parseInt(raw);
    const isPct = raw.includes('%');

    if (isNaN(isNum) || isNum === 0) return;

    let start     = 0;
    const end     = isNum;
    const duration = 800;
    const step    = 16;
    const inc     = end / (duration / step);

    const timer = setInterval(() => {
      start += inc;
      if (start >= end) {
        start = end;
        clearInterval(timer);
      }
      el.textContent = Math.round(start) + (isPct ? '%' : '');
    }, step);
  });

});
