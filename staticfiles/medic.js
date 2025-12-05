// static/medic.js
// ДОБАВЛЯЕМ пагинацию к существующему коду

async function apiFetch(path) {
  const r = await fetch(path, {
    credentials: 'same-origin',
    headers: {
      'Accept': 'application/json'
    }
  });
  if (!r.ok) throw new Error('api error ' + r.status);
  return r.json();
}

// === ДОБАВЛЕНО: переменные для пагинации ===
let currentPage = 1;
const ITEMS_PER_PAGE = 50;
let allLoadedUsers = []; // все загруженные пользователи
let filteredUsersForPagination = []; // отфильтрованные

(async function bootMedicUsersAllPages(){
  const API_ROOT = '/api/v1/medic/legacy-users/';
  const PAGE_SIZE = 1000;
  const tbody = document.getElementById('usersTbody');
  const searchInput = document.getElementById('searchInput');
  const filterBlood = document.getElementById('filterBlood');
  const filterCity = document.getElementById('filterCity');
  const btnRefresh = document.getElementById('btnRefresh');
  const btnExportCsv = document.getElementById('btnExportCsv');
  const btnExportXls = document.getElementById('btnExportXls');

  function renderRow(u) {
    return `<tr>
      <td>${u.user_id ?? ''}</td>
      <td>${(u.first_name||'') + ' ' + (u.last_name||'')}</td>
      <td>${u.blood_group||''}</td>
      <td>${u.iin||''}</td>
      <td>${u.city||''}</td>
      <td>${u.phone||''}</td>
      <td>${u.email||''}</td>
    </tr>`;
  }

  function buildFilters(data) {
    const bloodSet = new Set();
    const citySet = new Set();
    data.forEach(x => {
      if (x.blood_group) bloodSet.add(x.blood_group);
      if (x.city) citySet.add(x.city);
    });
    filterBlood.innerHTML = '<option value="">Все группы крови</option>';
    filterCity.innerHTML = '<option value="">Все города</option>';
    Array.from(bloodSet).sort().forEach(v => filterBlood.appendChild(new Option(v, v)));
    Array.from(citySet).sort().forEach(v => filterCity.appendChild(new Option(v, v)));
  }

  function filterData(items) {
    const q = (searchInput?.value || '').toLowerCase();
    const bf = filterBlood?.value || '';
    const cf = filterCity?.value || '';
    return items.filter(u => {
      if (bf && (u.blood_group||'') !== bf) return false;
      if (cf && (u.city||'') !== cf) return false;
      if (!q) return true;
      return ((u.first_name||'') + ' ' + (u.last_name||'') + ' ' + (u.iin||'') + ' ' + (u.email||'') + ' ' + (u.phone||'')).toLowerCase().includes(q);
    });
  }

  // === ИЗМЕНЕНО: рендерим только текущую страницу ===
  function tableFromData(items, resetPage = true) {
    filteredUsersForPagination = items;
    if (resetPage) {
      currentPage = 1; // сбрасываем только при фильтрации
    }
    renderCurrentPage();
  }

  // === ДОБАВЛЕНО: рендер текущей страницы ===
  function renderCurrentPage() {
    if (!filteredUsersForPagination || !filteredUsersForPagination.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="small-muted">Нет доноров / пользователей</td></tr>`;
      renderPagination(0, 0);
      return;
    }
    
    const totalPages = Math.ceil(filteredUsersForPagination.length / ITEMS_PER_PAGE);
    const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIdx = startIdx + ITEMS_PER_PAGE;
    const pageUsers = filteredUsersForPagination.slice(startIdx, endIdx);
    
    tbody.innerHTML = pageUsers.map(renderRow).join('');
    renderPagination(totalPages, filteredUsersForPagination.length);
  }

  // === ДОБАВЛЕНО: рендер пагинации ===
  function renderPagination(totalPages, totalItems) {
    let paginationBox = document.getElementById('paginationBox');
    
    if (!paginationBox) {
      paginationBox = document.createElement('div');
      paginationBox.id = 'paginationBox';
      document.querySelector('.content').appendChild(paginationBox);
    }
    
    if (totalPages <= 1) {
      paginationBox.innerHTML = '';
      return;
    }
    
    let html = '';
    
    html += `<button class="btn ghost" ${currentPage === 1 ? 'disabled' : ''} data-page="1">«</button>`;
    html += `<button class="btn ghost" ${currentPage === 1 ? 'disabled' : ''} data-page="${currentPage - 1}">‹</button>`;
    
    const maxButtons = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);
    
    if (endPage - startPage < maxButtons - 1) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }
    
    if (startPage > 1) {
      html += `<button class="btn ghost" data-page="1">1</button>`;
      if (startPage > 2) {
        html += `<span style="padding:0 8px; color:#999;">...</span>`;
      }
    }
    
    for (let i = startPage; i <= endPage; i++) {
      const isActive = i === currentPage;
      html += `<button class="btn ${isActive ? '' : 'ghost'}" ${isActive ? 'disabled' : ''} data-page="${i}">${i}</button>`;
    }
    
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        html += `<span style="padding:0 8px; color:#999;">...</span>`;
      }
      html += `<button class="btn ghost" data-page="${totalPages}">${totalPages}</button>`;
    }
    
    html += `<button class="btn ghost" ${currentPage === totalPages ? 'disabled' : ''} data-page="${currentPage + 1}">›</button>`;
    html += `<button class="btn ghost" ${currentPage === totalPages ? 'disabled' : ''} data-page="${totalPages}">»</button>`;
    
    const startItem = (currentPage - 1) * ITEMS_PER_PAGE + 1;
    const endItem = Math.min(currentPage * ITEMS_PER_PAGE, totalItems);
    html += `<span class="page-info">Показано ${startItem}–${endItem} из ${totalItems}</span>`;
    
    paginationBox.innerHTML = html;
    
    paginationBox.querySelectorAll('button[data-page]').forEach(btn => {
      btn.addEventListener('click', () => {
        const page = parseInt(btn.dataset.page);
        if (page >= 1 && page <= totalPages) {
          currentPage = page;
          renderCurrentPage();
          document.getElementById('tableWrap')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    });
  }

  function exportCsv(items, filename='users.csv') {
    const header = ['USER ID','FIO','BLOOD_GROUP','IIN','CITY','PHONE','EMAIL'];
    const rows = items.map(u => [
      u.user_id||'',
      `"${((u.first_name||'')+' '+(u.last_name||'')).replace(/"/g,'""')}"`,
      u.blood_group||'',
      u.iin||'',
      u.city||'',
      u.phone||'',
      u.email||''
    ].join(','));
    const csv = [header.join(','), ...rows].join('\r\n');
    const blob = new Blob([csv], {type: 'text/csv;charset=utf-8;'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click();
    a.remove(); URL.revokeObjectURL(url);
  }

  function exportXls(items, filename='users.xls') {
    exportCsv(items, filename);
  }

  async function fetchAllProgressive() {
    let url = `${API_ROOT}?page_size=${PAGE_SIZE}`;
    const all = [];
    while (url) {
      const r = await fetch(url, { credentials: 'same-origin' });
      if (!r.ok) {
        const txt = await r.text().catch(()=>'');
        throw new Error(`API error ${r.status} ${r.statusText} ${txt}`);
      }
      const json = await r.json();
      const results = Array.isArray(json) ? json : (json.results || []);
      all.push(...results);
      
      // === ИЗМЕНЕНО: показываем с пагинацией сразу ===
      allLoadedUsers = all;
      buildFilters(all);
      tableFromData(filterData(all), false); // НЕ сбрасываем страницу при подгрузке
      
      url = json.next || null;
      await new Promise(res => setTimeout(res, 0));
    }
    return all;
  }

  try {
    tbody.innerHTML = `<tr><td colspan="7" class="small-muted">Загрузка...</td></tr>`;
    
    const allItems = await fetchAllProgressive();
    allLoadedUsers = allItems;
    
    buildFilters(allItems);
    tableFromData(filterData(allItems));

    // === ИЗМЕНЕНО: перерендериваем с пагинацией при фильтрации ===
    if (btnRefresh) btnRefresh.addEventListener('click', () => tableFromData(filterData(allLoadedUsers)));
    if (searchInput) searchInput.addEventListener('input', () => tableFromData(filterData(allLoadedUsers)));
    if (filterBlood) filterBlood.addEventListener('change', () => tableFromData(filterData(allLoadedUsers)));
    if (filterCity) filterCity.addEventListener('change', () => tableFromData(filterData(allLoadedUsers)));

    if (btnExportCsv) btnExportCsv.addEventListener('click', () => {
      const shown = filterData(allLoadedUsers);
      exportCsv(shown, 'medic_users.csv');
    });
    if (btnExportXls) btnExportXls.addEventListener('click', () => {
      const shown = filterData(allLoadedUsers);
      exportXls(shown, 'medic_users.xls');
    });

  } catch (e) {
    console.error('load users error', e);
    tbody.innerHTML = `<tr><td colspan="7" class="small-muted">Ошибка загрузки</td></tr>`;
  }

})();

async function loadMedicUsersFromApi(page_size = 1000) {
  const url = `/api/v1/medic/legacy-users/?page_size=${page_size}`;
  const res = await fetch(url, { credentials: 'same-origin' });
  if (!res.ok) throw new Error('API error ' + res.status);
  const json = await res.json();
  return Array.isArray(json) ? json : (json.results || []);
}