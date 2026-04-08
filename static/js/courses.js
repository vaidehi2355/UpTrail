/* ── UpTrail — courses.js ────────────────────────────────────────────────── */
// MISSING_SKILLS injected by courses.html

const searchInput  = document.getElementById('searchInput');
const countLabel   = document.getElementById('countLabel');
const filterBtns   = document.querySelectorAll('.filter-btn');

let activeFilter = 'all';

// ── Platform filter ───────────────────────────────────────────────────────
filterBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    applyFilters();
  });
});

// ── Search ────────────────────────────────────────────────────────────────
searchInput.addEventListener('input', applyFilters);

// ── Apply both filters together ───────────────────────────────────────────
function applyFilters() {
  const query = searchInput.value.trim().toLowerCase();
  let visible = 0;

  // Check if we're in grouped view (platform sections) or single grid view
  const platformSections = document.querySelectorAll('.platform-section');

  if (platformSections.length > 0) {
    // Grouped view - filter by platform sections
    platformSections.forEach(section => {
      const sectionPlatform = section.dataset.platform.toLowerCase();
      const cards = section.querySelectorAll('.course-card');
      let sectionVisible = 0;

      // Check if this section matches the filter
      const matchPlatform = activeFilter === 'all' || sectionPlatform === activeFilter.toLowerCase();

      cards.forEach(card => {
        const matchSearch = !query || card.dataset.name.toLowerCase().includes(query);
        const show = matchPlatform && matchSearch;

        card.style.display = show ? '' : 'none';
        if (show) {
          sectionVisible++;
          visible++;
        }
      });

      // Hide/show entire section based on filter
      section.style.display = (matchPlatform && sectionVisible > 0) || activeFilter === 'all' ? '' : 'none';
    });
  } else {
    // Single grid view (personalized/relevance view)
    const coursesGrid = document.getElementById('coursesGrid');
    const cards = coursesGrid ? coursesGrid.querySelectorAll('.course-card') : [];

    cards.forEach(card => {
      const matchPlatform = activeFilter === 'all' ||
        card.dataset.platform.toLowerCase() === activeFilter.toLowerCase();
      const matchSearch = !query || card.dataset.name.toLowerCase().includes(query);
      const show = matchPlatform && matchSearch;

      card.style.display = show ? '' : 'none';
      if (show) visible++;
    });
  }

  if (countLabel) {
    countLabel.textContent = `${visible} course${visible !== 1 ? 's' : ''}`;
  }
}
