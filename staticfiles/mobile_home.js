// mobile_home.js
// Загружай этот файл динамически на мобильных (см. подсказку для base.html)

(function(){
  if (window.__bs_mobile_home_loaded) return;
  window.__bs_mobile_home_loaded = true;

  // ====== базовые utils ======
  const $ = sel => document.querySelector(sel);
  const byId = id => document.getElementById(id);

  const API = {
    config: '/api/v1/site/config/',
    hero:   '/api/v1/site/hero/',
    contacts:'/api/v1/contacts/',
    about:  '/api/v1/about/',
  };
  API.menu = '/api/v1/site/menu/';
  let menuCache = [];
  const LS_LANG = 'bs_lang';
  const getLang = ()=> localStorage.getItem(LS_LANG) || 'kk';
  const setLang = l => localStorage.setItem(LS_LANG, l);

  // ====== инициализация ======
  document.addEventListener('DOMContentLoaded', async () => {
    // Язык по умолчанию
    if (!localStorage.getItem(LS_LANG)) setLang('kk');
    highlightLang();
    setProfileTexts();

    // UI: бургер и профиль
    wireMenus();

    // загрузка данных
    await loadAll();
  });

  // вызови рендер при смене языка (после highlightLang())
  document.querySelectorAll('.lang-link').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      setLang(btn.dataset.lang);
      highlightLang();
      setProfileTexts();
      renderMenu();       // <— перерисовать подписи
      loadAll();          // остальное
    });
  });

  // === i18n для профиля ===
  const I18N = {
    account: { kk: 'Жеке кабинет', ru: 'Личный кабинет', en: 'Account' },
    logout:  { kk: 'Шығу',         ru: 'Выйти',          en: 'Logout'  },
  };

  function setProfileTexts(){
    const lang = getLang();
    const $acc = byId('accountLink');
    const $out = byId('logoutBtn');
    if ($acc) $acc.textContent = I18N.account[lang] || I18N.account.ru;
    if ($out) $out.textContent = I18N.logout[lang]  || I18N.logout.ru;
  }

  // ====== меню и профиль ======
  function wireMenus(){
    const burgerBtn = byId('burgerBtn');
    const flyMenu   = byId('flyMenu');
    const overlay   = byId('overlay');
    const profBtn   = byId('profileBtn');
    const profCard  = byId('profileCard');

    const oShow = show => {
      if (overlay) overlay.hidden = !show;
      if (flyMenu) flyMenu.hidden = !show;
    };
    burgerBtn?.addEventListener('click', ()=>{
      // закрыть профиль
      if (profCard) profCard.hidden = true;
      oShow(!overlay || overlay.hidden);
    });
    overlay?.addEventListener('click', ()=> oShow(false));

    profBtn?.addEventListener('click', ()=>{
      oShow(false);
      setProfileTexts();        // <— добавь
      if (profCard) profCard.hidden = !profCard.hidden;
    });

    // logout
    byId('logoutBtn')?.addEventListener('click', ()=>{
      // если используешь JWT — стереть токен
      localStorage.removeItem('token');
      window.location.href = '/home/';
    });
  }

  function highlightLang(){
    const current = getLang();
    document.querySelectorAll('.lang-link').forEach(b=>{
      b.classList.toggle('active', b.dataset.lang===current);
    });
  }

  // ====== загрузка API ======
  async function loadAll(){
    await Promise.all([
      loadConfig(),
      loadHero(),
      loadContacts(),
      loadAbout(),
      loadMenu() ,
      loadFooterText(),
    ]).catch(console.error);
  }

  async function loadConfig(){
    try{
      const r = await fetch(API.config);
      const x = await r.json();

      // логотип
      const logo = byId('logoImg');
      if (x.logo && logo) logo.src = x.logo;

      // приветствие
      const hello = byId('helloText');
      const lang = getLang();
      const helloMap = {
        kk: 'Қош келдіңіз, User',
        ru: 'Добро пожаловать, User',
        en: 'Welcome, User',
      };
      if (hello) hello.textContent = helloMap[lang] || helloMap.kk;

      // аватар (если есть в конфиге)
      const avatar = byId('avatarImg');
      const pAvatar = byId('pAvatar');
      const aSrc = x.avatar || '/static/img/avatar_default.png';
      if (avatar) avatar.src = aSrc;
      if (pAvatar) pAvatar.src = aSrc;

      // названия в футере (локализуем)
      const langVal = getLang();
      const supportTitle = byId('supportTitle');
      const emailTitle = byId('emailTitle');
      if (supportTitle) supportTitle.textContent = (langVal==='ru'?'Поддержка':langVal==='en'?'Support':'Қолдау');
      if (emailTitle) emailTitle.textContent   = (langVal==='ru'?'Эл. почта':langVal==='en'?'E-mail':'Эл. пошта');
    }catch(e){
      console.error('loadConfig error', e);
    }
  }

  async function loadHero(){
    try{
      const r = await fetch(API.hero);
      const d = await r.json();
      const lang = getLang();

      if (byId('heroTitle')) byId('heroTitle').textContent = d[`title_${lang}`] || d.title_ru || '';
      if (byId('heroSub')) byId('heroSub').textContent   = d[`subtitle_${lang}`] || d.subtitle_ru || '';
      if (d.image && byId('heroImg')) byId('heroImg').src = d.image;

      // промо
      if (byId('promoTitle')) byId('promoTitle').textContent = d[`promo_title_${lang}`] || (lang==='kk'?'BloodSeeker сіздің мобильді телефоныңызда': lang==='ru'?'BloodSeeker в твоем мобильном телефоне':'BloodSeeker on your phone');
      if (byId('promoSub')) byId('promoSub').textContent   = d[`promo_sub_${lang}`]   || (lang==='kk'?'Қолданбаны жүктеп алып, ыңғайлы қараңыз': lang==='ru'?'Скачай приложение и пользуйся удобно':'Download the app');
      if (d.promo_image && byId('promoImg')) byId('promoImg').src = d.promo_image;
    }catch(e){
      console.error('loadHero error', e);
    }
  }

  async function loadContacts(){
    try{
      const r = await fetch(API.contacts);
      const arr = await r.json();
      const phone = arr?.find(x=>x.kind==='phone')?.value || '+7 700 000 00 00';
      const email = arr?.find(x=>x.kind==='email')?.value || 'support@example.kz';
      if (byId('supportPhone')) byId('supportPhone').textContent = phone;
      if (byId('supportTel')) byId('supportTel').href = `tel:${phone.replace(/\s+/g,'')}`;
      if (byId('emailValue')) byId('emailValue').textContent = email;
      if (byId('supportMail')) byId('supportMail').href = `mailto:${email}`;
    }catch(e){
      console.error('loadContacts error', e);
    }
  }

  async function loadAbout(){
    try {
      const r = await fetch(API.about);
      const d = await r.json();
      const lang = getLang();

      const titleMap = { kk: 'Біз туралы', ru: 'О нас', en: 'About us' };
      const titleEl = byId('aboutTitle');
      if (titleEl) titleEl.textContent = titleMap[lang] ?? titleMap.ru;

      const html = d[`text_${lang}`] || '';
      const textEl = byId('aboutText');
      if (textEl) textEl.innerHTML = html;

      const imgEl = byId('aboutImg');
      if (imgEl) {
        const apiImg = (d.image || '').trim();
        imgEl.src = apiImg !== '' ? apiImg : '/static/about_us.png';
        imgEl.onerror = () => { imgEl.src = '/static/about_us.png'; };
        imgEl.alt = titleMap[lang] ?? 'About';
        imgEl.removeAttribute('hidden');
        imgEl.style.display = 'block';
      }
    } catch (e) {
      console.error('loadAbout error:', e);
      const imgEl = byId('aboutImg');
      if (imgEl) {
        imgEl.src = '/static/about_us.png';
        imgEl.onerror = null;
      }
    }
  }

  // загрузка меню из бекенда
  async function loadMenu(){
    try{
      const r = await fetch(API.menu);
      if(!r.ok) throw new Error('menu fetch failed');
      menuCache = await r.json();
      renderMenu();
    }catch(e){
      console.error(e);
      menuCache = [
        { key:'donate',  title_ru:'Сдача крови', title_kk:'Қан тапсыру', title_en:'Donate',  href:'/donate/' },
        { key:'bonuses', title_ru:'Бонусы',      title_kk:'Бонустар',    title_en:'Bonuses', href:'/bonuses/' },
        { key:'history', title_ru:'История',     title_kk:'Тарих',       title_en:'History', href:'/history/' },
      ];
      renderMenu();
    }
  }

  function renderMenu(){
    const box  = byId('flyMenu');
    if(!box) return;
    const lang = getLang();
    box.innerHTML = '';
    (menuCache || [])
      .filter(item => item.visible !== false)
      .sort((a,b)=> (a.order??0) - (b.order??0))
      .forEach(item=>{
        const title = item[`title_${lang}`] || item.title_ru || item.title_kk || item.title_en || item.key;
        const a = document.createElement('a');
        a.href = item.href || '#';
        a.textContent = title;
        box.appendChild(a);
      });
  }

  async function loadFooterText(){
    try{
      const r = await fetch(API.config);
      const x = await r.json();
      const lang = getLang();
      const text = x[`footer_text_${lang}`] || x.footer_text_ru || '';
      const el = byId('footerCopyright');
      if (el) el.textContent = text;
    }catch(e){
      console.error(e);
    }
  }

})();
