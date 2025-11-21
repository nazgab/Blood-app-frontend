// === helpers ===
const api = async (p) => {
  const r = await fetch(`/api/v1/${p}`, {
    credentials: 'same-origin',
    headers: {
      'Accept': 'application/json'
    }
  });
  if (!r.ok) {
    console.error(`API ${p} failed:`, r.status, r.statusText);
    return {};
  }
  return r.json().catch(() => ({}));
};

function buildMedicMenu(pop) {
  pop.innerHTML = `
    <nav class="medic-menu">
      <ul>
        <li class="group-title">Пользователи</li>
        <li class="menu-item"><a href="/admin/?app_label=core&model=profile">Пользователи</a></li>

        <li class="group-title">Донации</li>
        <li class="menu-item"><a href="/admin/donations/">Донации</a></li>
      </ul>
    </nav>
  `.trim();
}

// --- popover utils ---
function $id(id) { return document.getElementById(id); }
function inside(box, target) { return box && (box === target || box.contains(target)); }

function closeAllPopovers() {
  const mp = $id('menuPopover');
  const mb = $id('menuBackdrop');
  const pp = $id('profilePopover');
  const pb = $id('profileBackdrop');

  if (mp) mp.classList.add('hidden');
  if (mb) mb.classList.add('hidden');
  if (pp) pp.classList.add('hidden');
  if (pb) pb.classList.add('hidden');
}

// закрывать при прокрутке/ресайзе
window.addEventListener('scroll',  closeAllPopovers, { passive: true });
window.addEventListener('resize',  closeAllPopovers);

// закрывать при клике вне попапов и их триггеров
document.addEventListener('click', (e) => {
  const t = e.target;
  const inMenu    = inside($id('menuPopover'), t)    || inside(document.querySelector('.burger'), t);
  const inProfile = inside($id('profilePopover'), t) || inside(document.getElementById('profileBtn'), t);
  if (!inMenu && !inProfile) closeAllPopovers();
});


// === Языковая логика ===
let lang = document.documentElement.lang || 'kk';
const pick = (o, kk, ru, en) => {
  if (lang === 'kk') return o?.[kk];
  if (lang === 'ru') return o?.[ru];
  return o?.[en] || o?.[ru];
};

// i18n для профиля
const i18n = {
  profile: { kk: 'Жеке кабинет', ru: 'Личный кабинет', en: 'Account' },
  logout:  { kk: 'Шығу',         ru: 'Выйти',          en: 'Log out' }
};

const t = (key) => (i18n[key]?.[lang]) || i18n[key]?.ru || key;


// Настройки: логотип и футер
async function loadConfig() {
  const cfg = await api('site/config/');
  const logo = document.getElementById('logo');
  if (cfg.logo && logo) logo.src = cfg.logo;

  const footer = document.getElementById('footerText');
  if (footer) footer.textContent =
    pick(cfg, 'footer_text_kk', 'footer_text_ru', 'footer_text_en') || '';
}

// Герой
async function loadHero() {
  const hero = await api('site/hero/');
  const titleEl = document.getElementById('heroTitle');
  const subEl   = document.getElementById('heroSub');
  if (titleEl) titleEl.textContent = pick(hero, 'title_kk', 'title_ru', 'title_en') || '';
  if (subEl)   subEl.textContent   = pick(hero, 'subtitle_kk', 'subtitle_ru', 'subtitle_en') || '';

  const cta = document.getElementById('heroCta');
  if (cta) {
    cta.textContent = pick(hero, 'cta_text_kk', 'cta_text_ru', 'cta_text_en') || '';
    cta.href = hero.cta_url || '#';
  }
}


// Контакты (значения из админки)
// Контакты (для нижних карточек)
// Контакты (титулы и значения из админки)
async function loadContacts() {
  try {
    const res = await fetch('/api/v1/contacts/');
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.results || []);

    const phone = items.find(x => x.kind === 'phone');
    const email = items.find(x => x.kind === 'email');

    const phoneEl   = document.getElementById('contactPhone');
    const emailEl   = document.getElementById('contactEmail');
    const phoneTit  = document.getElementById('contactTitle');
    const emailTit  = document.getElementById('emailTitle');

    // значения
    if (phoneEl) phoneEl.textContent = phone ? phone.value : '';
    if (emailEl) emailEl.textContent = email ? email.value : '';

    // заголовки берем из label_kk / label_ru / label_en
    const phoneLabel = phone ? (lang === 'kk' ? phone.label_kk : lang === 'en' ? phone.label_en : phone.label_ru) : null;
    const emailLabel = email ? (lang === 'kk' ? email.label_kk : lang === 'en' ? email.label_en : email.label_ru) : null;

    // если в админке пусто — ставим разумный дефолт
    if (phoneTit) phoneTit.textContent = phoneLabel || (lang === 'kk' ? 'Байланыс' : lang === 'en' ? 'Contacts' : 'Контакты');
    if (emailTit) emailTit.textContent = emailLabel || 'Email';
  } catch (e) {
    console.error('Ошибка при загрузке контактов:', e);
  }
}

async function loadAbout() {
  try {
    const res = await fetch("/api/v1/about/");
    const data = await res.json();
    const textEl  = document.getElementById("aboutText");
    const titleEl = document.getElementById("aboutTitle");
    const text = data?.[`text_${lang}`] || data?.text_ru || '';
    if (textEl)  textEl.innerHTML = text;  // если приходит HTML из админки
    if (titleEl) titleEl.textContent = (lang === 'ru') ? "О нас" : (lang === 'kk') ? "Біз туралы" : "About us";
  } catch (e) {
    console.error("Ошибка загрузки блока О нас:", e);
  }
}


// Меню из API (site/menu/)
async function loadMenu() {
  const pop = document.getElementById('menuPopover');
  if (!pop) return;
  pop.innerHTML = '';

  // роль из body dataset (set в шаблоне)
  const role = document.body.dataset.role || 'user';

  if (role === 'medic') {
    // простое медик-меню — ровно два пункта
    const items = [
      { href: '/medic/users/', title: 'Пользователи' },
      { href: '/medic/donations/', title: 'Донации' }
    ];
    items.forEach(item => {
      const a = document.createElement('a');
      a.className = 'menu-item';
      a.href = item.href;
      a.textContent = item.title;
      pop.appendChild(a);
    });
    return;
  }
  if (document.body.dataset.role === 'medic') {
    pop.innerHTML = `
      <a class="menu-item" href="/medic/users/">Пользователи</a>
      <a class="menu-item" href="/medic/donations/">Донации</a>
    `;
    return;
  }
  // --- обычное поведение для пользователей: грузим из API ---
  const data = await api('site/menu/');
  const items = data.results || [];
  items.forEach(item => {
    const a = document.createElement('a');
    a.className = 'menu-item';
    a.href = item.href || '#';
    a.textContent = pick(item, 'title_kk', 'title_ru', 'title_en');
    pop.appendChild(a);
  });
}

async function loadMedicDonations() {
  if (window.location.pathname !== "/medic/donations/") return;
  const container = document.getElementById("donationsList");
  if (!container) return;
  const data = await api("medic/donations/");
  const rows = data.results || [];
  container.innerHTML = rows.length ? rows.map(d => `
    <div class="donation-item">
      <div><strong>ID:</strong> ${d.id}</div>
      <div><strong>User:</strong> ${d.user_id}</div>
      <div><strong>Date:</strong> ${d.date || d.created_at || ''}</div>
      <div><strong>Volume:</strong> ${d.volume || ''}</div>
    </div>
  `).join("") : "<p>Нет доноров / донаций</p>";
}
document.addEventListener("DOMContentLoaded", () => { loadMedicDonations(); });

// Выход
function handleLogout() {
  try {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
  } catch (_) {}
  // серверный логаут (очистит сессию Django):
  window.location.href = '/accounts/logout/?next=/';
}


// Локализация заголовков в карточках футера
function setContactTitlesByLang() {
  const t1 = document.getElementById('contactTitle');
  const t2 = document.getElementById('emailTitle');
  if (t1) t1.textContent = (lang === 'kk') ? 'Байланыс' : (lang === 'en') ? 'Contacts' : 'Контакты';
  if (t2) t2.textContent = 'Email';
}

function setWelcomeByLang() {
  const wrap = document.getElementById('welcomeText');
  if (!wrap) return;

  const nameEl = document.getElementById('userName');
  const username = nameEl ? nameEl.textContent.trim() : 'User';

  // если пользователь не залогинен, разметку трогать не будем — сервер сам показал ссылку "Кіру / Войти"
  const isAuthed = !!document.getElementById('userNameRight') || !!document.getElementById('userName');
  if (!isAuthed) return;

  // ищем текстовый узел до/после спана и меняем только его
  // формат: "Добро пожаловать, " + <span id="userName">...</span>
  const prefix = (lang === 'kk') ? 'Қош келдіңіз, '
               : (lang === 'en') ? 'Welcome, '
               : 'Добро пожаловать, ';

  // перерисуем содержимое, но сохраним <span id="userName">
  wrap.innerHTML = `${prefix}<span id="userName">${username}</span>`;
}

function setPromoByLang() {
  const t = document.getElementById('promoTitle');
  const s = document.getElementById('promoSub');
  if (!t || !s) return;

  const texts = {
    kk: {
      title: 'BloodSeeker сіздің мобильді телефоныңызда',
      sub: 'Қолданбаны жүктеп алып, ыңғайлы қараңыз'
    },
    ru: {
      title: 'BloodSeeker в твоем мобильном телефоне',
      sub: 'Скачай приложение для более удобного просмотра'
    },
    en: {
      title: 'BloodSeeker on your mobile phone',
      sub: 'Download the app for more convenient viewing'
    }
  };

  t.textContent = texts[lang]?.title || texts.ru.title;
  s.textContent = texts[lang]?.sub || texts.ru.sub;
}

// === bindings ===
function bindLang() {
  const buttons = document.querySelectorAll('.lang-link');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      lang = btn.dataset.lang || 'kk';
      refresh();

      // если профильный попап открыт — перестроим его с новыми подписями
      const profilePop = document.getElementById('profilePopover');
      if (profilePop && !profilePop.classList.contains('hidden')) {
        buildProfilePopover();
      }
    });
  });

  // выставить активную кнопку при первоначальной загрузке
  buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.lang === lang));
}


function bindBurger() {
  const burger = document.querySelector('.burger');
  const pop = document.getElementById('menuPopover');
  const backdrop = document.getElementById('menuBackdrop');
  if (!burger || !pop || !backdrop) return;

  function positionPopover() {
    const r = burger.getBoundingClientRect();
    pop.style.left = `${r.left + r.width + 12}px`;
    pop.style.top  = `${Math.max(8, r.top - 6)}px`;
  }
  function openMenu() {
    pop.classList.remove('hidden');
    backdrop.classList.remove('hidden');
    requestAnimationFrame(positionPopover);
  }
  function closeMenu() {
    pop.classList.add('hidden');
    backdrop.classList.add('hidden');
  }

  burger.addEventListener('click', (e) => {
    e.stopPropagation();
    if (pop.classList.contains('hidden')) openMenu(); else closeMenu();
  });
  backdrop.addEventListener('click', closeMenu);
  window.addEventListener('resize', () => { if (!pop.classList.contains('hidden')) positionPopover(); });
  window.addEventListener('scroll',  () => { if (!pop.classList.contains('hidden')) { 
  pop.classList.add('hidden'); 
  backdrop.classList.add('hidden'); 
  }});
}

// Профильное меню
function buildProfilePopover() {
  const pop = document.getElementById('profilePopover');
  if (!pop) return;

  const avatarEl = document.querySelector('#profileBtn .avatar') || document.querySelector('.avatar');
  const nameEl     = document.getElementById('userNameRight') || document.getElementById('userName');
  const avatarSrc  = avatarEl ? avatarEl.src : '';
  const displayName = nameEl ? nameEl.textContent.trim() : 'User';

  pop.innerHTML = `
    <div class="profile-head">
      <img src="${avatarSrc}" alt="" style="width:28px;height:28px;border-radius:50%;object-fit:cover;border:1px solid #ddd">
      <div class="ph-name">${displayName}</div>
    </div>
    <a href="/profile/" class="profile-item" id="profileLink">${t('profile')}</a>
    <button 
      type="button" 
      class="profile-item" 
      id="profileLogoutBtn"
      style="background:none;border:none;cursor:pointer;color:#e53935;font-weight:500">
      ${t('logout')}
    </button>

  `;

  const logoutBtn = document.getElementById('profileLogoutBtn');
  if (logoutBtn) logoutBtn.addEventListener('click', handleLogout);
}


function bindProfileMenu() {
  const trigger  = document.getElementById('profileBtn');      // ← было .querySelector('.user')
  const pop      = document.getElementById('profilePopover');
  const backdrop = document.getElementById('profileBackdrop');
  if (!trigger || !pop || !backdrop) return;

  function positionPopover() {
    const r = trigger.getBoundingClientRect();
    const left = r.left + (r.width / 2) - 140;
    pop.style.left = `${Math.max(12, left)}px`;
    pop.style.top  = `${r.bottom + 8}px`;
  }
  function openMenu() {
    buildProfilePopover();
    pop.classList.remove('hidden');
    backdrop.classList.remove('hidden');
    requestAnimationFrame(positionPopover);
  }
  function closeMenu() {
    pop.classList.add('hidden');
    backdrop.classList.add('hidden');
  }

  trigger.addEventListener('click', (e) => {
    e.stopPropagation();
    if (pop.classList.contains('hidden')) openMenu(); else closeMenu();
  });
  backdrop.addEventListener('click', closeMenu);
  window.addEventListener('resize', () => { if (!pop.classList.contains('hidden')) positionPopover(); });
  window.addEventListener('scroll',  () => { if (!pop.classList.contains('hidden')) closeMenu(); });
}

document.getElementById('menuPopover')?.addEventListener('click', function(e){
  const a = e.target.closest('a');
  if (!a) return;
  const href = a.getAttribute('href') || '#';
  // закроем меню визуально
  document.getElementById('menuPopover').classList.add('hidden');
  document.getElementById('menuBackdrop').classList.add('hidden');

  // если это API-путь — подгрузим JSON и покажем в простом модальном окошке (вложи свою реализацию)
  if (href.startsWith('/api/v1/')) {
    e.preventDefault();
    api(href.replace('/api/v1/','')).then(json=>{
      // очень простой modal: можешь заменить render на свою функцию
      const s = JSON.stringify(json, null, 2);
      alert(s); // временно — потом заменим на красивый modal
    }).catch(err => alert('Ошибка API: ' + err));
  }
  // иначе — браузер перейдёт по href сам (сначала меню закрыли)
});

// === boot ===
async function refresh() {
  setWelcomeByLang(); // локализуем приветствие
  setContactTitlesByLang(); // локализуем заголовки футера
  setPromoByLang(); // локализуем промо-блок
  await Promise.all([
    loadConfig(),
    loadHero(),
    loadContacts(),
    loadMenu(),
    loadAbout(),
  ]);
}

bindProfileMenu();
bindLang();
bindBurger();
refresh().catch(e => console.error(e));
