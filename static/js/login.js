/* ── UpTrail — login.js ──────────────────────────────────────────────────── */

function switchTab(tab) {
  const isLogin = tab === 'login';

  document.getElementById('form-login').style.display  = isLogin ? 'block' : 'none';
  document.getElementById('form-signup').style.display = isLogin ? 'none'  : 'block';

  document.getElementById('tab-login').classList.toggle('active',  isLogin);
  document.getElementById('tab-signup').classList.toggle('active', !isLogin);
}
