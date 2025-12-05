/* bonuses.js
   Обновлённый единый файл:
   - Полный переключатель языков (KK / RU / EN) — сохраняет выбор в localStorage
   - Применяет переводы к заголовкам, подзаголовкам, футеру, кнопкам и лоадеру
   - НЕ трогает остальной функционал (fetchBonuses, обработчики кнопок и т.д.)
*/

/* ============================
   ========== CONFIG ==========
   ============================ */

const supportedLangs = ['kk', 'ru', 'en'];
const LS_KEY = 'bs_lang'; // ключ в localStorage для языка

/* ============================
   ====== TRANSLATIONS ========
   ============================ */

/*
  Добавляйте сюда ключи и переводы. Ключи должны соответствовать id или
  классу (используем getElementById или querySelector('.className')) ниже.
*/
const TRANSLATIONS = {
  // Пример: id/contactTitle -> переводы
  contactTitle: { kk: 'Байланыс', ru: 'Контакты', en: 'Contacts' },
  emailTitle:   { kk: 'Email',     ru: 'Email',     en: 'Email' },
  footerText:   { kk: '© 2025 BloodSeeker. Барлық құқықтар қорғалған.', ru: '© 2025 BloodSeeker. Все права защищены.', en: '© 2025 BloodSeeker. All rights reserved.' },
  promoTitle:   { kk: 'BloodSeeker сіздің мобильді телефоныңыз', ru: 'BloodSeeker в твоем мобильном телефоне', en: 'BloodSeeker on your mobile phone' },
  promoSub:     { kk: 'Қолданбаны жүктеп алып, ыңғайлы қараңыз', ru: 'Скачай приложение для более удобного просмотра', en: 'Download the app for more convenient viewing' },
  heroTitle:    { kk: 'Қан тапсырыңыз - өмірді сақтаңыз!', ru: 'Сдайте кровь - подарите жизнь!', en: 'Donate blood — save a life!' },
  heroSub:      { kk: 'Тіркеліп, ең жақын орталықты табыңыз', ru: 'Зарегистрируйтесь и найдите ближайший центр', en: 'Register and find the nearest center' },
  aboutTitle:   { kk: 'Біз туралы', ru: 'О нас', en: 'About us' },
  spendTitle:   { kk: 'Не нәрсеге жұмсау', ru: 'На что потратить', en: 'Where to spend' },
  bonusSub:     { kk: 'Жаңарту деректері…', ru: 'Загружаем данные...', en: 'Loading data...' },
  profileLabel: { kk: 'Профиль', ru: 'Профиль', en: 'Profile' },
  welcomeText:  { kk: 'Қош келдіңіз,', ru: 'Добро пожаловать,', en: 'Welcome,' },
  // Дополнительные кнопки/лейблы
  btnLoadMore:  { kk: 'Тағы жүктеу', ru: 'Загрузить ещё', en: 'Load more' },
  btnSpend:     { kk: 'Шығаруға', ru: 'Потратить', en: 'Spend' },
  loaderText:   { kk: 'Жүктелуде…', ru: 'Загрузка…', en: 'Loading…' }
};

/* ============================
   ======= LANG HELPERS =======
   ============================ */

function getLang(){
  // порядок приоритета: localStorage -> html.lang -> 'kk'
  const fromLS = localStorage.getItem(LS_KEY);
  if (fromLS && supportedLangs.includes(fromLS)) return fromLS;
  const fromHtml = document.documentElement.lang;
  if (fromHtml && supportedLangs.includes(fromHtml)) return fromHtml;
  return 'kk';
}

function setLang(lang){
  if (!supportedLangs.includes(lang)) lang = 'ru';
  localStorage.setItem(LS_KEY, lang);
  document.documentElement.lang = lang;

  // визуальная пометка кнопок (на странице у вас должны быть элементы с классом .lang-link и data-lang)
  document.querySelectorAll('.lang-link').forEach(btn => {
    const btnLang = btn.dataset.lang || btn.getAttribute('data-lang');
    if (btnLang) btn.classList.toggle('active', btnLang === lang);
  });

  // применяем переводы: простые и полные
  applySimpleTranslations(lang);
  applyFullTranslations(lang);
}

function initLangSwitcher(){
  // ожидаем наличие .lang-link элементов; если нет — ничего страшного
  document.querySelectorAll('.lang-link').forEach(btn => {
    const data = btn.dataset.lang || btn.getAttribute('data-lang');
    if (!data) return;
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      setLang(data);
    });
  });

  // применяем выбранный или дефолтный язык при загрузке
  setLang(getLang());
}

/* ============================
   ======= APPLY TEXTS ========
   ============================ */

function safeSetTextById(id, text, { html=false } = {}){
  if (!id) return;
  let el = document.getElementById(id);
  if (!el) el = document.querySelector('.' + id); // fallback на класс
  if (!el) return;
  if (html) el.innerHTML = text;
  else el.textContent = text;
}

function applySimpleTranslations(lang){
  // Этот набор обычно минимальный и уже мог быть в старом файле.
  safeSetTextById('welcomeText', (TRANSLATIONS.welcomeText && TRANSLATIONS.welcomeText[lang]) || '');
  safeSetTextById('profileLabel', (TRANSLATIONS.profileLabel && TRANSLATIONS.profileLabel[lang]) || '');
  safeSetTextById('spendTitle', (TRANSLATIONS.spendTitle && TRANSLATIONS.spendTitle[lang]) || '');
  // loader чтобы был при вызове fetch
  const loader = document.getElementById('loader') || document.querySelector('.loader');
  if (loader) loader.textContent = (TRANSLATIONS.loaderText && TRANSLATIONS.loaderText[lang]) || '';
}

function applyFullTranslations(lang){
  // Базовые текстовые элементы
  for (const key of Object.keys(TRANSLATIONS)){
    const val = TRANSLATIONS[key][lang] || TRANSLATIONS[key].ru || '';
    // Ожидаем, что id в HTML совпадают с ключами транслейшна
    safeSetTextById(key, val);
  }

  // Дополнительные элементы, которые могут быть в вашем шаблоне с другими id/классами
  // Footer
  const footer = document.querySelector('footer');
  if (footer) {
    // если в footer есть элемент с id footerText - уже установили. Иначе - попробуем найти .footer-text
    if (!document.getElementById('footerText') && footer.querySelector('.footer-text')) {
      footer.querySelector('.footer-text').textContent = TRANSLATIONS.footerText[lang] || TRANSLATIONS.footerText.ru;
    }
  }

  // promo
  if (!document.getElementById('promoTitle') && document.querySelector('.promo .title')) {
    document.querySelectorAll('.promo .title').forEach(el => el.textContent = TRANSLATIONS.promoTitle[lang] || TRANSLATIONS.promoTitle.ru);
  }
  if (!document.getElementById('promoSub') && document.querySelector('.promo .sub')) {
    document.querySelectorAll('.promo .sub').forEach(el => el.textContent = TRANSLATIONS.promoSub[lang] || TRANSLATIONS.promoSub.ru);
  }

  // hero
  if (!document.getElementById('heroTitle') && document.querySelector('.hero .title')) {
    document.querySelectorAll('.hero .title').forEach(el => el.textContent = TRANSLATIONS.heroTitle[lang] || TRANSLATIONS.heroTitle.ru);
  }
  if (!document.getElementById('heroSub') && document.querySelector('.hero .sub')) {
    document.querySelectorAll('.hero .sub').forEach(el => el.textContent = TRANSLATIONS.heroSub[lang] || TRANSLATIONS.heroSub.ru);
  }

  // Кнопки
  document.querySelectorAll('[data-i18n]').forEach(el => {
    // data-i18n содержит ключ перевода, например data-i18n="btnLoadMore"
    const key = el.dataset.i18n;
    if (!key) return;
    const txt = (TRANSLATIONS[key] && TRANSLATIONS[key][lang]) || (TRANSLATIONS[key] && TRANSLATIONS[key].ru) || '';
    if (txt) {
      if (el.tagName.toLowerCase() === 'input' || el.tagName.toLowerCase() === 'button') el.value ? el.value = txt : el.textContent = txt;
      else el.textContent = txt;
    }
  });
}



let bonusesData = [];
let bonusesPage = 1;
let bonusesPerPage = 10;
let isLoading = false;

async function fetchBonuses({ page = 1, perPage = bonusesPerPage } = {}){
  // Сохраняем loader и показываем его
  const loader = document.getElementById('loader') || document.querySelector('.loader');
  if (loader) loader.style.display = '';

  isLoading = true;
  try {
    // Попробуем обратиться к API, если его нет — вернём моковые данные
    let res, json;
    try {
      res = await fetch(`/api/bonuses?page=${page}&per_page=${perPage}`, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('network');
      json = await res.json();
    } catch (e) {
      // mock: если нет бэкенда локально — создаём тестовые бонусы
      json = {
        results: Array.from({length: perPage}, (_, i) => ({
          id: (page-1)*perPage + i + 1,
          title: `Бонус ${(page-1)*perPage + i + 1}`,
          amount: Math.floor(Math.random() * 5000),
          date: new Date().toLocaleDateString()
        })),
        next: page < 5 ? `/api/bonuses?page=${page+1}` : null
      };
    }

    // append или replace
    if (page === 1) {
      bonusesData = json.results || [];
    } else {
      bonusesData = bonusesData.concat(json.results || []);
    }

    renderBonuses(bonusesData);
    bonusesPage = page;
  } finally {
    isLoading = false;
    if (loader) loader.style.display = 'none';
  }
}

function renderBonuses(list){
  const container = document.getElementById('bonusesList') || document.querySelector('.bonuses-list');
  if (!container) return;

  container.innerHTML = '';
  if (!list || list.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty';
    const lang = getLang();
    empty.textContent = (lang === 'kk' ? 'Бонустар табылған жоқ' : lang === 'en' ? 'No bonuses found' : 'Бонусов не найдено');
    container.appendChild(empty);
    return;
  }

  for (const b of list){
    const item = document.createElement('div');
    item.className = 'bonus-item';
    item.innerHTML = `
      <div class="bonus-title">${escapeHtml(b.title || '')}</div>
      <div class="bonus-amount">${escapeHtml(String(b.amount || '0'))}</div>
      <div class="bonus-date">${escapeHtml(b.date || '')}</div>
      <button class="btn-spend" data-bonus-id="${b.id}" data-i18n="btnSpend">${TRANSLATIONS.btnSpend[getLang()]}</button>
    `;
    container.appendChild(item);
  }

  // Повесим обработчики на кнопки "Потратить"
  container.querySelectorAll('.btn-spend').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = btn.dataset.bonusId;
      onSpendBonus(id);
    });
  });
}

function onSpendBonus(bonusId){
  // Лёгкий обработчик — можно подставить вашу логику
  alert((getLang() === 'kk') ? `Бонус #${bonusId} жұмсалады` : (getLang() === 'en') ? `Spending bonus #${bonusId}` : `Тратите бонус #${bonusId}`);
}

/* ============================
   ======= HELPERS ============
   ============================ */

function escapeHtml(str){
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/* ============================
   ====== INIT / BINDING ======
   ============================ */

function initPage(){
  initLangSwitcher();

  // повесим на кнопку "Загрузить ещё" (если есть)
  const btnMore = document.getElementById('btnLoadMore') || document.querySelector('.btn-load-more');
  if (btnMore) {
    btnMore.addEventListener('click', (e) => {
      e.preventDefault();
      if (isLoading) return;
      fetchBonuses({ page: bonusesPage + 1 });
    });
    // установить текст кнопки в локализации
    btnMore.dataset.i18n = btnMore.dataset.i18n || 'btnLoadMore';
  }

  // если есть форма или профиль — обработаем минимально
  const profileBtn = document.getElementById('profileBtn') || document.querySelector('.profile-btn');
  if (profileBtn) {
    profileBtn.addEventListener('click', (e) => {
      e.preventDefault();
      // ваш код открытия профиля...
      console.log('open profile (stub)');
    });
  }

  // initial fetch
  fetchBonuses({ page: 1 });

  // применить переводы к элементам, у которых стоит data-i18n
  applyFullTranslations(getLang());
}

// Автоинициализация при DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPage);
} else {
  initPage();
}

/* ============================
   ======= END OF FILE ========
   ============================ */
