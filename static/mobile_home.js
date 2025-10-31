// ====== базовые utils ======
const $ = sel => document.querySelector(sel);
const byId = id => document.getElementById(id);

const API = {
  config: '/api/v1/site/config/',
  hero:   '/api/v1/site/hero/',
  contacts:'/api/v1/contacts/',
  about:  '/api/v1/about/',
};

const LS_LANG = 'bs_lang';
const getLang = ()=> localStorage.getItem(LS_LANG) || 'kk';
const setLang = l => localStorage.setItem(LS_LANG, l);

// ====== инициализация ======
document.addEventListener('DOMContentLoaded', async () => {
  // Язык по умолчанию
  if (!localStorage.getItem(LS_LANG)) setLang('kk');
  highlightLang();

  // Слушатели языка
  document.querySelectorAll('.lang-link').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      setLang(btn.dataset.lang);
      highlightLang();
      loadAll(); // перерисовать тексты
    });
  });

  // UI: бургер и профиль
  wireMenus();

  // загрузка данных
  await loadAll();
});

// ====== меню и профиль ======
function wireMenus(){
  const burgerBtn = byId('burgerBtn');
  const flyMenu   = byId('flyMenu');
  const overlay   = byId('overlay');
  const profBtn   = byId('profileBtn');
  const profCard  = byId('profileCard');

  const oShow = show => {
    overlay.hidden = !show;
    flyMenu.hidden = !show;
  };
  burgerBtn?.addEventListener('click', ()=>{
    // закрыть профиль
    profCard.hidden = true;
    oShow(!overlay || overlay.hidden);
  });
  overlay?.addEventListener('click', ()=> oShow(false));

  profBtn?.addEventListener('click', ()=>{
    // закрыть меню
    oShow(false);
    profCard.hidden = !profCard.hidden;
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
    loadAbout()
  ]).catch(console.error);
}

async function loadConfig(){
  const r = await fetch(API.config);
  const x = await r.json();

  // логотип
  const logo = byId('logoImg');
  if (x.logo) logo.src = x.logo;

  // приветствие
  const hello = byId('helloText');
  const lang = getLang();
  const helloMap = {
    kk: 'Қош келдіңіз, User',
    ru: 'Добро пожаловать, User',
    en: 'Welcome, User',
  };
  hello.textContent = helloMap[lang] || helloMap.kk;

  // аватар (если есть в конфиге)
  const avatar = byId('avatarImg');
  const pAvatar = byId('pAvatar');
  const aSrc = x.avatar || '/static/img/avatar_default.png';
  avatar.src = aSrc; pAvatar.src = aSrc;

  // названия в футере (локализуем)
  byId('supportTitle').textContent = (lang==='ru'?'Поддержка':lang==='en'?'Support':'Қолдау');
  byId('emailTitle').textContent   = (lang==='ru'?'Эл. почта':lang==='en'?'E-mail':'Эл. пошта');
}

async function loadHero(){
  const r = await fetch(API.hero);
  const d = await r.json();
  const lang = getLang();

  byId('heroTitle').textContent = d[`title_${lang}`] || d.title_ru || '';
  byId('heroSub').textContent   = d[`subtitle_${lang}`] || d.subtitle_ru || '';
  if (d.image) byId('heroImg').src = d.image;

  // промо (используем те же данные, если есть отдельные — подставь свой эндпоинт)
  byId('promoTitle').textContent = d[`promo_title_${lang}`] || (lang==='kk'?'BloodSeeker сіздің мобильді телефоныңызда': lang==='ru'?'BloodSeeker в твоем мобильном телефоне':'BloodSeeker on your phone');
  byId('promoSub').textContent   = d[`promo_sub_${lang}`]   || (lang==='kk'?'Қолданбаны жүктеп алып, ыңғайлы қараңыз': lang==='ru'?'Скачай приложение и пользуйся удобно':'Download the app');
  if (d.promo_image) byId('promoImg').src = d.promo_image;
}

async function loadContacts(){
  const r = await fetch(API.contacts);
  const arr = await r.json();
  const phone = arr?.find(x=>x.kind==='phone')?.value || '+7 700 000 00 00';
  const email = arr?.find(x=>x.kind==='email')?.value || 'support@example.kz';
  byId('supportPhone').textContent = phone;
  byId('supportTel').href = `tel:${phone.replace(/\s+/g,'')}`;
  byId('emailValue').textContent = email;
  byId('supportMail').href = `mailto:${email}`;
}

async function loadAbout(){
  const r = await fetch(API.about);
  const d = await r.json();
  const lang = getLang();
  byId('aboutTitle').textContent = d[`title_${lang}`] || d.title_ru || '';
  const html = d[`text_${lang}`] || '';
  // безопасно вставляем (бэкенд даёт проверенный html)
  byId('aboutText').innerHTML = html;
  if (d.image) byId('aboutImg').src = d.image;
}
