/* ── UpTrail — roles.js ──────────────────────────────────────────────────── */

const rolesGrid    = document.getElementById('rolesGrid');
const resultsCount = document.getElementById('resultsCount');
const filterBtns   = document.querySelectorAll('.filter-btn');

// ── Filter logic ──────────────────────────────────────────────────────────
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    applyFilter(btn.dataset.filter);
  });
});

function applyFilter(type) {
  const cards = rolesGrid ? rolesGrid.querySelectorAll('.role-card') : [];
  let visible = 0;

  cards.forEach(card => {
    const pct = parseInt(card.dataset.pct) || 0;
    let show = true;

    if      (type === 'high') show = pct >= 60;
    else if (type === 'mid')  show = pct >= 20 && pct < 60;
    else if (type === 'low')  show = pct < 20;
    // 'all' always shows everything

    card.style.display = show ? '' : 'none';
    if (show) visible++;
  });

  if (resultsCount) {
    resultsCount.textContent = `${visible} role${visible !== 1 ? 's' : ''} found`;
  }
}

// ── Animate progress bars on load ─────────────────────────────────────────
// Bars start at 0 width in CSS; we trigger the CSS transition after a short
// delay so the animation plays visibly when the page loads.
document.addEventListener('DOMContentLoaded', () => {
  const fills = document.querySelectorAll('.prog-fill');
  fills.forEach(fill => {
    const target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => { fill.style.width = target; }, 120);
  });
});
