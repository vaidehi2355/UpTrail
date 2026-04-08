/* ── UpTrail — resume_analyser.js ────────────────────────────────────────── */

const dropZone    = document.getElementById('dropZone');
const fileInput   = document.getElementById('fileInput');
const fileSelected = document.getElementById('fileSelected');
const fileNameEl  = document.getElementById('fileName');
const analyseBtn  = document.getElementById('analyseBtn');
const resumeForm  = document.getElementById('resumeForm');

// ── Drag and drop ─────────────────────────────────────────────────────────
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('drag');
});

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag');
});

dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag');
  const file = e.dataTransfer.files[0];
  if (file) {
    // Assign to file input
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    showFile(file.name);
  }
});

// ── File input change ─────────────────────────────────────────────────────
function handleFileSelect(input) {
  if (input.files && input.files[0]) {
    showFile(input.files[0].name);
  }
}

function showFile(name) {
  dropZone.style.display    = 'none';
  fileSelected.style.display = 'flex';
  fileNameEl.textContent    = name;
  analyseBtn.disabled       = false;
}

function clearFile() {
  dropZone.style.display     = 'block';
  fileSelected.style.display = 'none';
  fileInput.value            = '';
  analyseBtn.disabled        = true;
}

// ── Loading state on submit ───────────────────────────────────────────────
resumeForm.addEventListener('submit', () => {
  analyseBtn.textContent = 'Analysing…';
  analyseBtn.disabled    = true;
});

// ── Animate score number counting up ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const scoreEl = document.getElementById('scoreNum');
  if (!scoreEl) return;

  const raw = scoreEl.textContent.trim();
  const num = parseInt(raw);
  if (isNaN(num)) return;

  let current    = 0;
  const duration = 900;
  const step     = 16;
  const inc      = num / (duration / step);

  scoreEl.textContent = '0';

  const timer = setInterval(() => {
    current += inc;
    if (current >= num) {
      current = num;
      clearInterval(timer);
    }
    scoreEl.textContent = Math.round(current);
  }, step);
});
