/* bonuses.js — unified, ready to paste
   - Translations for KK / RU / EN (only targeted labels)
   - Burger menu + profile popover (robust)
   - Partners clickable
   - fetchBonuses() (preserves server messages / doesn't overwrite history-empty unless necessary)
   - Extra fix to ensure .small-label .balance-label .spend-title translate
*/

/* ========= TRANSLATIONS ========= */
const LANG = {
  kk: {
    welcome: "Қош келдіңіз,",
    bonuses: "Бонустар",
    balance_title: "Жиналған бонус",
    spend_title: "Не нәрсеге жұмсауға болады",
    footer_phone: "Қолдау",
    footer_email: "Эл. пошта",
    partner_magnum: "Magnum",
    partner_sulpak: "Sulpak",
    partner_fresh: "Fresh",
    copyright: "© 2025 BloodSeeker. Барлық құқықтар қорғалған."
  },
  ru: {
    welcome: "Добро пожаловать,",
    bonuses: "Бонусы",
    balance_title: "Накоплено бонусов",
    spend_title: "На что потратить",
    footer_phone: "Поддержка",
    footer_email: "Эл. почта",
    partner_magnum: "Magnum",
    partner_sulpak: "Sulpak",
    partner_fresh: "Fresh",
    copyright: "© 2025 BloodSeeker. Все права защищены."
  },
  en: {
    welcome: "Welcome,",
    bonuses: "Bonuses",
    balance_title: "Accumulated bonuses",
    spend_title: "Where to spend",
    footer_phone: "Support",
    footer_email: "Email",
    partner_magnum: "Magnum",
    partner_sulpak: "Sulpak",
    partner_fresh: "Fresh",
    copyright: "© 2025 BloodSeeker. All rights reserved."
  }
};

/* ========= HELPERS ========= */
function qs(sel){ try{ return document.querySelector(sel); }catch(e){return null;} }
function qsa(sel){ try{ return Array.from(document.querySelectorAll(sel)); }catch(e){return [];} }

function getSavedLang(){
  return localStorage.getItem('app_lang') || localStorage.getItem('bs_lang') || document.documentElement.lang || 'ru';
}
function saveLang(code){
  localStorage.setItem('app_lang', code);
}

/* ========= APPLY LANGUAGE (targeted elements only) ========= */
function applyLanguage(code){
  const t = LANG[code] || LANG.ru;

  // Banner / page title
  const pageTitle = qs('#pageTitle') || qs('.banner-title') || qs('[data-i18n="bonuses"]');
  if(pageTitle) pageTitle.textContent = t.bonuses;

  // Banner subtitle (do not overwrite long server text) — only if data-i18n present
  const pageSub = qs('#pageSub') || qs('.promo-sub') || qs('[data-i18n="pageSub"]');
  if(pageSub && pageSub.dataset && pageSub.dataset.i18n !== undefined) pageSub.textContent = (t.pageSub || pageSub.textContent);

  // Welcome prefix — preserve user name
  const welcomeWrap = qs('#welcomeText');
  const nameEl = qs('#userNameRight') || qs('#userName');
  if(welcomeWrap){
    if(nameEl && nameEl.textContent.trim()){
      welcomeWrap.innerHTML = `${t.welcome} <span id="${nameEl.id||''}">${nameEl.textContent.trim()}</span>`;
    } else {
      welcomeWrap.textContent = t.welcome;
    }
  }

  // Balance label (targeted)
  const balanceLabel = qs('#yourBonusesLabel') || qs('.balance-label') || qs('[data-i18n="balance_title"]') || qs('.balance-meta');
  if(balanceLabel) balanceLabel.textContent = t.balance_title;

  // Spend section title
  const spendTitle = qs('#spendTitle') || qs('.spend-title') || qs('[data-i18n="spend_title"]');
  if(spendTitle) spendTitle.textContent = t.spend_title;

  // Partners — prefer data-part attributes, fallback by index
  qsa('.spend-item').forEach((el, idx) => {
    const label = el.querySelector('div');
    const part = el.dataset.part || el.dataset.i18nPart || null;
    if(!label) return;
    if(part === 'magnum') label.textContent = t.partner_magnum;
    else if(part === 'sulpak') label.textContent = t.partner_sulpak;
    else if(part === 'fresh') label.textContent = t.partner_fresh;
    else {
      // fallback by order
      if(idx === 0) label.textContent = t.partner_magnum;
      if(idx === 1) label.textContent = t.partner_sulpak;
      if(idx === 2) label.textContent = t.partner_fresh;
    }
  });

  // Footer titles
  const contactTitle = qs('#contactTitle') || (qsa('.footer-title')[0] || null);
  if(contactTitle) contactTitle.textContent = t.footer_phone;
  const emailTitle = qs('#emailTitle') || (qsa('.footer-title')[1] || null);
  if(emailTitle) emailTitle.textContent = t.footer_email;

  // Copyright
  const copyEl = qs('.copyright');
  if(copyEl) copyEl.textContent = t.copyright;

  // mark active language button
  qsa('.lang-link').forEach(b => b.classList.toggle('active', b.dataset.lang === code));

  saveLang(code);
}

/* ========= EXTRA FIX: ensure specific selectors are translated ========= */
(function extraFixModule(){
  const EXTRA = {
    kk: { small_label: 'Бонустар', balance_label: 'Жиналған бонус', spend_title: 'Не нәрсеге жұмсауға болады' },
    ru: { small_label: 'Бонусы', balance_label: 'Накоплено бонусов', spend_title: 'На что потратить' },
    en: { small_label: 'Bonuses', balance_label: 'Accumulated bonuses', spend_title: 'Where to spend' }
  };

  function applyExtraFor(lang){
    const t = EXTRA[lang] || EXTRA.ru;
    const elSmall = qs('.small-label');
    if(elSmall) elSmall.textContent = t.small_label;
    const elBal = qs('.balance-label') || qs('#yourBonusesLabel');
    if(elBal) elBal.textContent = t.balance_label;
    const elSpend = qs('.spend-title') || qs('#spendTitle');
    if(elSpend) elSpend.textContent = t.spend_title;
  }

  document.addEventListener('DOMContentLoaded', ()=>{
    const saved = getSavedLang();
    applyExtraFor(saved);
    // Attach to language buttons to update immediately after other handlers
    qsa('.lang-link').forEach(btn=>{
      btn.addEventListener('click', function(){
        const code = this.dataset.lang || saved;
        // small delay so main applyLanguage (if present) runs first
        setTimeout(()=>{ applyExtraFor(code); }, 10);
      });
    });
  });
})();

/* ========= BURGER MENU ========= */
function initBurger(){
  const btn = qs('.burger');
  const pop = qs('#menuPopover');
  const back = qs('#menuBackdrop');
  if(!btn || !pop || !back) return;

  pop.style.display = 'none';
  back.style.display = 'none';

  if(!pop.innerHTML.trim()){
    pop.innerHTML = `
      <a class="menu-item" href="/">Главная</a>
      <a class="menu-item" href="/donation/">Сдача крови</a>
      <a class="menu-item" href="/bonuses/">Бонусы</a>
      <a class="menu-item" href="/history/">История</a>
    `;
  }

  function show(){
    const r = btn.getBoundingClientRect();
    pop.style.position = 'absolute';
    pop.style.left = (r.left + window.scrollX) + 'px';
    pop.style.top = (r.bottom + window.scrollY + 8) + 'px';
    pop.style.display = 'block';
    back.style.display = 'block';
    pop.style.zIndex = 9999;
    back.style.zIndex = 9998;
  }
  function hide(){
    pop.style.display = 'none';
    back.style.display = 'none';
  }

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    if(pop.style.display === 'block') hide(); else show();
  });
  back.addEventListener('click', hide);
  document.addEventListener('click', function(e){
    if(!pop.contains(e.target) && !btn.contains(e.target)) hide();
  });
}

/* ========= PROFILE POPOVER ========= */
function initProfilePopover(){
  const btn = qs('#profileBtn');
  const pop = qs('#profilePopover');
  const back = qs('#profileBackdrop');
  if(!btn || !pop || !back) return;

  pop.style.display = 'none';
  back.style.display = 'none';
  pop.style.maxWidth = '280px';
  pop.style.overflow = 'hidden';

  function build(){
    const avatar = qs('#profileBtn .avatar') ? qs('#profileBtn .avatar').src : '';
    const name = (qs('#userNameRight') || qs('#userName')) ? (qs('#userNameRight') || qs('#userName')).textContent.trim() : 'User';
    pop.innerHTML = `
      <div style="padding:12px;">
        <div style="display:flex;gap:10px;align-items:center;">
          <img src="${avatar}" style="width:44px;height:44px;border-radius:8px;border:1px solid #eee;object-fit:cover">
          <div style="font-weight:600">${name}</div>
        </div>
        <hr style="margin:10px 0;border-top:1px solid #f0f0f0">
        <a class="profile-item" href="/profile/" style="display:block;padding:8px 10px;color:#222;text-decoration:none;">Профиль</a>
        <a class="profile-item" href="/accounts/logout/?next=/" style="display:block;padding:8px 10px;color:#d32;text-decoration:none;font-weight:700;">Выйти</a>
      </div>
    `;
  }

  function show(){
    build();
    const r = btn.getBoundingClientRect();
    pop.style.position = 'absolute';
    pop.style.left = (r.left + window.scrollX) + 'px';
    pop.style.top = (r.bottom + window.scrollY + 8) + 'px';
    pop.style.display = 'block';
    back.style.display = 'block';
    pop.style.zIndex = 9999;
    back.style.zIndex = 9998;
  }
  function hide(){
    pop.style.display = 'none';
    back.style.display = 'none';
  }

  btn.addEventListener('click', function(e){
    e.stopPropagation();
    if(pop.style.display === 'block') hide(); else show();
  });
  back.addEventListener('click', hide);
  document.addEventListener('click', function(e){
    if(!pop.contains(e.target) && !btn.contains(e.target)) hide();
  });
}

/* ========= PARTNERS CLICKABLE ========= */
function initPartners(){
  qsa('.spend-item[data-href]').forEach(el=>{
    el.style.cursor = 'pointer';
    el.addEventListener('click', ()=> {
      const href = el.dataset.href;
      if(href) window.location.href = href;
    });
  });
}

/* ========= FETCH BONUSES (safe) ========= */
async function fetchBonuses(){
  const bonusValueEl = qs('#bonusValue');
  const bonusSubEl = qs('#bonusSub');
  const bonusListEl = qs('#bonusList');

  if(!bonusValueEl || !bonusListEl) return;

  try{
    const res = await fetch('/api/v1/bonuses/me/', {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' }
    });

    if(!res.ok){
      bonusValueEl.textContent = '—';
      if(bonusSubEl) bonusSubEl.textContent = '';
      return;
    }

    const data = await res.json();
    const balance = (data.balance !== undefined) ? data.balance : (data.points || 0);
    bonusValueEl.textContent = Number(balance).toFixed(2);
    if(bonusSubEl) bonusSubEl.textContent = data.last_updated ? ('Обновлено: ' + new Date(data.last_updated).toLocaleString()) : '';

    const history = data.history || data.transactions || [];
    if(history.length === 0){
      // keep existing HTML "no history" message if present (do not overwrite)
      if(bonusListEl.children.length === 0) {
        bonusListEl.innerHTML = '<div class="muted">История начислений отсутствует.</div>';
      }
      return;
    }

    bonusListEl.innerHTML = '';
    history.forEach(item=>{
      const created = item.created_at || item.date || item.ts || '';
      const note = item.note || item.kind || item.type || 'Операция';
      const amount = item.amount || item.delta || item.points || 0;
      const node = document.createElement('div');
      node.className = 'bonus-item';
      node.innerHTML = `
        <div>
          <div style="font-weight:600;">${note}</div>
          <div class="muted">${created ? new Date(created).toLocaleString() : ''}</div>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:600;">${Number(amount).toFixed(2)}</div>
          <div class="muted">баллов</div>
        </div>`;
      bonusListEl.appendChild(node);
    });

  }catch(err){
    console.error('fetchBonuses error', err);
    if(bonusValueEl) bonusValueEl.textContent = '—';
    if(bonusSubEl) bonusSubEl.textContent = '';
  }
}

/* ========= INIT ========= */
document.addEventListener('DOMContentLoaded', function(){
  // apply language from saved preference or default
  const saved = getSavedLang();
  applyLanguage(saved);

  // attach language buttons
  qsa('.lang-link').forEach(btn=>{
    btn.addEventListener('click', function(){
      const code = this.dataset.lang || 'ru';
      applyLanguage(code);
      // small delay to let other handlers run, then extra fix already applied inside applyLanguage
      setTimeout(()=>{ /* extra fix module also listens to buttons */ }, 10);
    });
  });

  // init UI
  initBurger();
  initProfilePopover();
  initPartners();
  fetchBonuses();

  // expose for debug
  window.BloodSeeker = window.BloodSeeker || {};
  window.BloodSeeker.setLang = applyLanguage;
  window.BloodSeeker.getLang = getSavedLang;
  window.BloodSeeker.fetchBonuses = fetchBonuses;
});
