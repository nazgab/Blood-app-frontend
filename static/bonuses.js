/* bonuses.js — исправленная версия
   2025 — применимо для вашего bonuses.html
   (заменяет предыдущий bonuses.js)
*/

(function(){
  // ---------- Вспомогательные ----------
  function qs(sel){ return document.querySelector(sel); }
  function qsa(sel){ return Array.from(document.querySelectorAll(sel)); }

  // ---------- TRANSLATIONS ----------
  const supportedLangs = ['kk','ru','en'];
  const LS_KEY = 'bs_lang';

  const TRANSLATIONS = {
    balanceLabel: { kk: 'Жиналған бонустар', ru: 'Накоплено бонусов', en: 'Accumulated bonuses' },
    bonusSubDefault: { kk: 'Жаңарту деректері…', ru: 'Загружаем данные.', en: 'Loading data...' },
    loaderText: { kk: '', ru: '', en: '' },
    spendTitle: { kk: 'Не нәрсеге жұмсау', ru: 'На что потратить', en: 'Where to spend' },
    contactTitle: { kk: 'Байланыс', ru: 'Контакты', en: 'Contacts' },
    emailTitle:   { kk: 'Эл. почта', ru: 'Email', en: 'Email' },
    footerText:   { kk: '© 2025 BloodSeeker. Барлық құқықтар қорғалған.', ru: '© 2025 BloodSeeker. Все права защищены.', en: '© 2025 BloodSeeker. All rights reserved.' },
    partners: {
      'Magnum': { kk: 'Magnum', ru: 'Magnum', en: 'Magnum' },
      'Sulpak': { kk: 'Sulpak', ru: 'Sulpak', en: 'Sulpak' },
      'Fresh':  { kk: 'Fresh',  ru: 'Fresh',  en: 'Fresh' }
    },
    // дополнительные строки
    welcome: { kk: 'Қош келдіңіз,', ru: 'Добро пожаловать,', en: 'Welcome,' },
    profile: { kk: 'Жеке кабинет', ru: 'Личный кабинет', en: 'Account' },
    logout:  { kk: 'Шығу', ru: 'Выйти', en: 'Log out' },
    btnSpend: { kk: 'Потратить', ru: 'Потратить', en: 'Spend' },
    btnLoadMore: { kk: 'Тағы жүктеу', ru: 'Загрузить ещё', en: 'Load more' }
  };

  // ---------- Lang helpers ----------
  function getLang(){
    const ls = localStorage.getItem(LS_KEY);
    if (ls && supportedLangs.includes(ls)) return ls;
    const htmlLang = document.documentElement.lang;
    if (htmlLang && supportedLangs.includes(htmlLang)) return htmlLang;
    return 'ru';
  }

  function setLang(l){
    if (!supportedLangs.includes(l)) l = 'ru';
    localStorage.setItem(LS_KEY, l);
    document.documentElement.lang = l;
    // визуально выделить кнопку
    qsa('.lang-link').forEach(b => {
      const btnLang = b.dataset.lang || b.getAttribute('data-lang');
      b.classList.toggle('active', btnLang === l);
    });
    applyTranslations(l);
  }

  function initLangSwitcher(){
    qsa('.lang-link').forEach(btn=>{
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const lang = btn.dataset.lang || btn.getAttribute('data-lang');
        if (lang) setLang(lang);
      });
    });
    // применим текущий
    setLang(getLang());
  }

  // ---------- Apply translations ----------
  function safeSetText(selectorOrEl, text, { html=false } = {}){
    if (!selectorOrEl) return;
    let el = typeof selectorOrEl === 'string' ? document.querySelector(selectorOrEl) : selectorOrEl;
    if (!el) return;
    if (html) el.innerHTML = text;
    else el.textContent = text;
  }

  function applyTranslations(lang){
    // balance label
    const balLabel = qs('.balance-visual .balance-label') || qs('.balance-label') || qs('#balanceLabel');
    if (balLabel) balLabel.textContent = TRANSLATIONS.balanceLabel[lang] || TRANSLATIONS.balanceLabel.ru;

    // bonusSub: если в нём стоит системный текст — безопасно заменить, если там "Обновлено: ..." — лучше сохранить дату
    const bonusSub = qs('#bonusSub') || qs('.bonus-sub');
    if (bonusSub) {
      const cur = (bonusSub.textContent || '').trim();
      // если текст уже содержит "Обновлено:" — оставим (только если языки совпадают можно переводить)
      if (!cur || cur === TRANSLATIONS.bonusSubDefault.ru || cur === TRANSLATIONS.bonusSubDefault.en || cur === TRANSLATIONS.bonusSubDefault.kk) {
        bonusSub.textContent = TRANSLATIONS.bonusSubDefault[lang] || TRANSLATIONS.bonusSubDefault.ru;
      } else {
        // если там "Обновлено: ..." — переведём префикс "Обновлено:" в нужный язык, сохраним дату
        const m = cur.match(/(Обновлено:|Updated:|Жаңартылды:)\s*(.*)/i);
        if (m) {
          const datePart = m[2] || '';
          const prefix = (lang === 'kk') ? 'Жаңартылды:' : (lang === 'en') ? 'Updated:' : 'Обновлено:';
          bonusSub.textContent = (datePart ? (prefix + ' ' + datePart) : prefix);
        }
      }
    }

    // loader
    const loader = qs('#loader') || qs('.loader');
    if (loader) loader.textContent = TRANSLATIONS.loaderText[lang] || TRANSLATIONS.loaderText.ru;

    // spend title
    const spend = qs('#spendTitle') || qs('.spend-title');
    if (spend) spend.textContent = TRANSLATIONS.spendTitle[lang] || TRANSLATIONS.spendTitle.ru;

    // partners labels: у вас .spend-grid .spend-item > div
    qsa('.spend-item').forEach(item=>{
      const nameDiv = item.querySelector('div');
      if (!nameDiv) return;
      // сохраняем оригинал в data-orig, чтобы знать ключ
      if (!nameDiv.dataset.orig) nameDiv.dataset.orig = (nameDiv.textContent || '').trim();
      const key = nameDiv.dataset.orig;
      if (key && TRANSLATIONS.partners[key]) {
        nameDiv.textContent = TRANSLATIONS.partners[key][lang] || TRANSLATIONS.partners[key].ru;
      }
    });

    // footer titles
    const cTitle = qs('#contactTitle');
    const eTitle = qs('#emailTitle');
    const footerText = qs('#footerText') || qs('.copyright');
    if (cTitle) cTitle.textContent = TRANSLATIONS.contactTitle[lang] || TRANSLATIONS.contactTitle.ru;
    if (eTitle) eTitle.textContent = TRANSLATIONS.emailTitle[lang] || TRANSLATIONS.emailTitle.ru;
    if (footerText) footerText.textContent = TRANSLATIONS.footerText[lang] || TRANSLATIONS.footerText.ru;

    // simple strings: welcome / profile popover
    const welcomeWrap = qs('#welcomeText');
    if (welcomeWrap) {
      // если есть #userName или #userNameRight — покажем "Welcome, Name"
      const nameEl = qs('#userName') || qs('#userNameRight');
      if (nameEl && nameEl.textContent.trim()) {
        welcomeWrap.innerHTML = `${TRANSLATIONS.welcome[lang]} <span id="userName">${nameEl.textContent.trim()}</span>`;
      } // else — оставим что сервер вставил
    }

    // profile popover re-render
    buildProfilePopover();

    // buttons / data-i18n (если есть)
    qsa('[data-i18n]').forEach(el=>{
      const key = el.dataset.i18n;
      if (!key) return;
      const txt = (TRANSLATIONS[key] && TRANSLATIONS[key][lang]) || (TRANSLATIONS[key] && TRANSLATIONS[key].ru) || '';
      if (!txt) return;
      if (el.tagName.toLowerCase() === 'input' || el.tagName.toLowerCase() === 'button') {
        el.value ? el.value = txt : el.textContent = txt;
      } else el.textContent = txt;
    });
  }

  // Expose global helper so inline fetch can call it (if needed)
  window.bs_applyBonusesLang = function(lang){
    const l = lang || getLang();
    applyTranslations(l);
  };

  // ---------- Burger / Profile / Partners (оставляем вашу логику) ----------
  function initBurger(){
    const btn = qs('.burger');
    const pop = qs('#menuPopover');
    const back = qs('#menuBackdrop');
    if(!btn) return;
    btn.addEventListener('click', ()=> {
      pop && pop.classList.toggle('hidden');
      back && back.classList.toggle('hidden');
    });
    if(back) back.addEventListener('click', ()=> {
      pop && pop.classList.add('hidden');
      back.classList.add('hidden');
    });
  }

  const localStrings = {
    profile: TRANSLATIONS.profile,
    logout: TRANSLATIONS.logout
  };

  function buildProfilePopover(){
    const pop = qs('#profilePopover');
    if(!pop) return;
    if(!qs('#userNameRight') && !qs('#userName')) return;
    const avatar = qs('#profileBtn .avatar') ? qs('#profileBtn .avatar').src : '';
    const displayName = (qs('#userNameRight') || qs('#userName')) ? (qs('#userNameRight') || qs('#userName')).textContent.trim() : 'User';
    const lang = getLang();
    pop.innerHTML = `
      <div class="profile-card">
        <div class="profile-row" style="display:flex;gap:10px;align-items:center;">
          <img class="avatar" src="${avatar}" alt="" style="width:44px;height:44px;border-radius:8px;object-fit:cover">
          <div>
            <div class="name" style="font-weight:600">${displayName}</div>
            <div class="muted" style="font-size:13px">${(qs('#userName')||qs('#userNameRight'))? (qs('#userName')||qs('#userNameRight')).textContent : ''}</div>
          </div>
        </div>
        <hr style="margin:10px 0">
        <nav class="profile-menu">
          <a href="/profile/" class="profile-link">${localStrings.profile[lang]}</a>
          <a href="/accounts/logout/?next=/" class="profile-link danger">${localStrings.logout[lang]}</a>
        </nav>
      </div>
    `;
  }

  function initProfilePopover(){
    const btn = qs('#profileBtn');
    const pop = qs('#profilePopover');
    const back = qs('#profileBackdrop');
    if(!btn || !pop) return;
    btn.addEventListener('click', ()=> {
      pop.classList.toggle('hidden');
      back && back.classList.toggle('hidden');
      if(!pop.classList.contains('hidden')) buildProfilePopover();
    });
    if(back) back.addEventListener('click', ()=> { pop.classList.add('hidden'); back.classList.add('hidden'); });
  }

  function initPartnersLinks(){
    qsa('.spend-item').forEach(el=>{
      const href = el.dataset.href;
      if(!href) return;
      el.style.cursor = 'pointer';
      el.addEventListener('click', ()=> window.open(href, '_blank'));
    });
  }

  // ---------- Wrap fetchBonuses if exists ----------
  function wrapFetchBonuses(){
    if (typeof window.fetchBonuses !== 'function') {
      return;
    }
    const original = window.fetchBonuses;
    // replace with wrapper that ensures translations reapply after fetch completes
    window.fetchBonuses = async function(...args){
      try {
        const res = original.apply(this, args);
        // if original returns a promise — await it
        if (res && typeof res.then === 'function') {
          await res;
        }
      } catch (err) {
        // swallow: original handles errors
        console.warn('fetchBonuses wrapper: original threw', err);
      } finally {
        // small delay to allow DOM updates, затем применим локализацию
        setTimeout(()=> {
          try { window.bs_applyBonusesLang(); } catch(e){ console.warn(e); }
        }, 40);
      }
    };
  }

  // ---------- Initialization ----------
  document.addEventListener('DOMContentLoaded', ()=>{
    initBurger();
    initLangSwitcher();
    initProfilePopover();
    initPartnersLinks();

    // Если fetchBonuses определён — оборачиваем его, чтобы после каждого вызова перевод применялся
    wrapFetchBonuses();

    // Если fetchBonuses существует, запускаем его (как раньше) — но обычно это делает inline-скрипт
    // Применим переводы при загрузке (на случай, если сервер уже вставил тексты)
    setTimeout(()=> {
      try { window.bs_applyBonusesLang(); } catch(e){ console.warn(e); }
    }, 60);
    // и ещё одна попытка через небольшую задержку (с запасом)
    setTimeout(()=> {
      try { window.bs_applyBonusesLang(); } catch(e){ console.warn(e); }
    }, 600);
  });

  // Expose helpers for console
  window.BloodSeeker = window.BloodSeeker || {};
  window.BloodSeeker.setLang = setLang;
  window.BloodSeeker.getLang = getLang;
  window.BloodSeeker.applyLang = window.bs_applyBonusesLang;

})();
