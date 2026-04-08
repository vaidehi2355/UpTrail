/* ── UpTrail — home.js ───────────────────────────────────────────────────── */
// Depends on SKILLS_DATA and INITIAL_SKILLS injected by home.html

const selected = new Set(INITIAL_SKILLS);

// ── DOM refs ──────────────────────────────────────────────────────────────
const countBadge    = document.getElementById('countBadge');
const selectedTags  = document.getElementById('selectedTags');
const hiddenInputs  = document.getElementById('hiddenInputs');
const proceedBtn    = document.getElementById('proceedBtn');
const proceedHint   = document.getElementById('proceedHint');
const searchInput   = document.getElementById('searchInput');
const searchClear   = document.getElementById('searchClear');
const noResults     = document.getElementById('noResults');
const noResultsQ    = document.getElementById('noResultsQuery');

// ── Toggle a skill chip ───────────────────────────────────────────────────
function toggleSkill(el) {
  const skill = el.dataset.skill;
  if (selected.has(skill)) {
    selected.delete(skill);
    el.classList.remove('selected');
  } else {
    selected.add(skill);
    el.classList.add('selected');
  }
  renderSidebar();
}

// ── Remove a tag from the sidebar ─────────────────────────────────────────
function removeTag(skill) {
  selected.delete(skill);

  // Deselect the chip in the left panel
  const chip = document.querySelector(`.skill-chip[data-skill="${CSS.escape(skill)}"]`);
  if (chip) chip.classList.remove('selected');

  renderSidebar();
}

// ── Render sidebar tags + hidden inputs + button state ───────────────────
function renderSidebar() {
  const count = selected.size;

  // Badge
  countBadge.textContent = count;

  // Tags
  if (count === 0) {
    selectedTags.innerHTML = '<div class="empty-sel" id="emptyMsg">Click skills on the left<br>to add them here.</div>';
  } else {
    selectedTags.innerHTML = [...selected].map(skill => `
      <span class="sel-tag" data-skill="${skill}">
        ${skill}
        <span class="sel-tag-rm" onclick="removeTag('${escapeHtml(skill)}')">✕</span>
      </span>
    `).join('');
  }

  // Hidden inputs for form submission
  hiddenInputs.innerHTML = [...selected]
    .map(skill => `<input type="hidden" name="skills" value="${escapeHtml(skill)}">`)
    .join('');

  // Proceed button + hint — no minimum, always enabled
  if (count === 0) {
    proceedBtn.disabled = false;
    proceedHint.textContent = `No skills selected — we'll show all roles`;
    proceedHint.classList.remove('ready');
  } else {
    proceedBtn.disabled = false;
    proceedHint.textContent = `${count} skill${count !== 1 ? 's' : ''} selected — good to go!`;
    proceedHint.classList.add('ready');
  }
}

// ── Search / filter ───────────────────────────────────────────────────────
searchInput.addEventListener('input', function () {
  const q = this.value.trim().toLowerCase();

  // Show / hide clear button
  if (q.length > 0) {
    searchClear.classList.add('visible');
  } else {
    searchClear.classList.remove('visible');
  }

  let anyVisible = false;

  document.querySelectorAll('.domain-section').forEach(section => {
    let sectionHasVisible = false;

    section.querySelectorAll('.skill-chip').forEach(chip => {
      const match = chip.dataset.skill.toLowerCase().includes(q);
      chip.classList.toggle('hidden', !match);
      if (match) sectionHasVisible = true;
    });

    section.style.display = sectionHasVisible ? '' : 'none';
    if (sectionHasVisible) anyVisible = true;
  });

  // No results state
  if (!anyVisible && q.length > 0) {
    noResults.style.display = 'block';
    noResultsQ.textContent = this.value.trim();
  } else {
    noResults.style.display = 'none';
  }
});

function clearSearch() {
  searchInput.value = '';
  searchInput.dispatchEvent(new Event('input'));
  searchInput.focus();
}

// ── Escape helper (prevent XSS in dynamic HTML) ───────────────────────────
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Init: sync chip states with server-restored skills ───────────────────
document.addEventListener('DOMContentLoaded', () => {
  if (INITIAL_SKILLS.length > 0) {
    INITIAL_SKILLS.forEach(skill => {
      const chip = document.querySelector(`.skill-chip[data-skill="${CSS.escape(skill)}"]`);
      if (chip) chip.classList.add('selected');
    });
    renderSidebar();
  }
});
