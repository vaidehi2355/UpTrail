/* ── UpTrail — internship.js ─────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {

  const searchInput = document.getElementById('searchInput');
  const countLabel = document.getElementById('countLabel');

  // ── Animate progress bars ─────────────────────────────────────────────
  document.querySelectorAll('.prog-fill').forEach(fill => {
    const target = fill.style.width;
    fill.style.width = '0%';
    setTimeout(() => { fill.style.width = target; }, 150);
  });

  // ── Animate mini stat numbers counting up ─────────────────────────────
  document.querySelectorAll('.mini-num').forEach(el => {
    const raw = el.textContent.trim();
    const num = parseInt(raw);
    if (isNaN(num) || num === 0) return;

    let current  = 0;
    const duration = 600;
    const step     = 16;
    const inc      = num / (duration / step);

    const timer = setInterval(() => {
      current += inc;
      if (current >= num) {
        current = num;
        clearInterval(timer);
      }
      el.textContent = Math.round(current);
    }, step);
  });

  // ── Search functionality ───────────────────────────────────────────────
  if (searchInput) {
    searchInput.addEventListener('input', applySearch);
  }

  function applySearch() {
    const query = searchInput.value.trim().toLowerCase();
    let visible = 0;

    // Check if we're in grouped view (role sections) or single list view
    const roleSections = document.querySelectorAll('.role-section');

    if (roleSections.length > 0) {
      // Grouped view - search across all sections
      roleSections.forEach(section => {
        const cards = section.querySelectorAll('.intern-card');
        let sectionVisible = 0;

        cards.forEach(card => {
          const title = card.querySelector('.intern-title')?.textContent.toLowerCase() || '';
          const company = card.querySelector('.company-name')?.textContent.toLowerCase() || '';
          const location = card.querySelector('.location')?.textContent.toLowerCase() || '';

          const matchSearch = !query || title.includes(query) || company.includes(query) || location.includes(query);
          const show = matchSearch;

          card.style.display = show ? '' : 'none';
          if (show) {
            sectionVisible++;
            visible++;
          }
        });

        // Hide section if no matches
        section.style.display = sectionVisible > 0 ? '' : 'none';
      });
    } else {
      // Single list view
      const internCards = document.querySelectorAll('.intern-card');

      internCards.forEach(card => {
        const title = card.querySelector('.intern-title')?.textContent.toLowerCase() || '';
        const company = card.querySelector('.company-name')?.textContent.toLowerCase() || '';
        const location = card.querySelector('.location')?.textContent.toLowerCase() || '';

        const matchSearch = !query || title.includes(query) || company.includes(query) || location.includes(query);
        const show = matchSearch;

        card.style.display = show ? '' : 'none';
        if (show) visible++;
      });
    }

    if (countLabel) {
      countLabel.textContent = `${visible} found`;
    }
  }

  // ── Toggle show more/less skills ──────────────────────────────────────
  document.querySelectorAll('.show-more-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const internshipId = btn.dataset.internshipId;
      const container = document.querySelector(`.intern-skills[data-internship-id="${internshipId}"]`);
      const hiddenSkills = container.querySelectorAll('.hidden-skill');
      const isExpanded = btn.dataset.expanded === 'true';

      hiddenSkills.forEach(skill => {
        skill.style.display = isExpanded ? 'none' : 'inline-block';
      });

      btn.dataset.expanded = !isExpanded;
      btn.textContent = isExpanded ? `+${hiddenSkills.length} more` : 'Show less';
    });
  });

});
