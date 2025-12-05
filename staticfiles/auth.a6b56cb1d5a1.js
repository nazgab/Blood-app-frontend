// показать/скрыть пароль
document.addEventListener('click', (e)=>{
  const btn = e.target.closest('[data-toggle-pass]');
  if(!btn) return;
  const input = btn.parentElement.querySelector('input');
  if(!input) return;
  input.type = (input.type === 'password') ? 'text' : 'password';
  btn.textContent = (input.type === 'password') ? '👁' : '🙈';
});

// подставить логотип из SiteConfig
(async ()=>{
  try{
    const r = await fetch('/api/v1/site/config/');
    const cfg = await r.json();
    const logo = document.getElementById('brandLogo');
    if(logo && cfg.logo) logo.src = cfg.logo;
  }catch(_){}
})();
