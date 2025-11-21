// static/medic.js
// минимальная логика: загрузка /api/v1/legacy/users/ + фильтры + экспорт

async function apiFetch(path) {
  const r = await fetch(path, {
    credentials: 'same-origin',   // <-- важно, чтобы sessionid кука ушла на сервер
    headers: {
      'Accept': 'application/json'
    }
  });
  if (!r.ok) throw new Error('api error ' + r.status);
  return r.json();
}


// вставьте в static/medic.js — заменяет старый boot / load users код
(async function bootMedicUsersAllPages(){
  const API_ROOT = '/api/v1/medic/legacy-users/';
  const PAGE_SIZE = 1000; // можно увеличить, но 1000 — обычно нормально
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
    // очистим старые опции (кроме пустой)
    filterBlood.innerHTML = '<option value="">Все группы</option>';
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

  function tableFromData(items) {
    if (!items || !items.length) {
      tbody.innerHTML = `<tr><td colspan="7" class="small-muted">Нет доноров / пользователей</td></tr>`;
      return;
    }
    tbody.innerHTML = items.map(renderRow).join('');
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
    // простая версия — отдать CSV, Excel откроет
    exportCsv(items, filename);
  }

    // --- fetch all pages ---
    // --- efficient fetchAll: fetch first page, render, then parallel fetch remaining ---
    async function fetchAllParallel(API_ROOT, PAGE_SIZE, onPartial) {
        // 1) fetch first page
        const firstUrl = `${API_ROOT}?page_size=${PAGE_SIZE}`;
        const firstResp = await fetch(firstUrl, { credentials: 'same-origin' });
        if (!firstResp.ok) {
            const txt = await firstResp.text().catch(()=>'');
            throw new Error(`API error ${firstResp.status} ${txt}`);
        }
        const firstJson = await firstResp.json();
        const firstResults = Array.isArray(firstJson) ? firstJson : (firstJson.results || []);
        const all = [...firstResults];

        // call back so UI can show immediate results
        if (typeof onPartial === 'function') onPartial(all, { partial: true });

        // 2) if count <= firstResults.length -> done
        const total = (typeof firstJson.count === 'number') ? firstJson.count : null;
        if (!total || all.length >= total) {
            return all;
        }

        // 3) compute pages to fetch (DRF uses page param)
        // pages are: ?page=2,3,... with same page_size
        const pages = Math.ceil(total / PAGE_SIZE);
        const remainingPages = [];
        for (let p = 2; p <= pages; p++) remainingPages.push(p);

        // 4) create parallel fetch promises (but don't overload: chunk them)
        const CHUNK = 6; // degree of parallelism — tweak if needed
        for (let i = 0; i < remainingPages.length; i += CHUNK) {
            const chunk = remainingPages.slice(i, i + CHUNK);
            const promises = chunk.map(p => {
            const url = `${API_ROOT}?page=${p}&page_size=${PAGE_SIZE}`;
            return fetch(url, { credentials: 'same-origin' })
                .then(r => {
                    if (!r.ok) return r.text().then(t => { throw new Error(`API ${r.status}: ${t}`); });
                return r.json();
            })
                .then(json => Array.isArray(json) ? json : (json.results || []))
                .catch(err => {
                    console.error('page fetch failed', url, err);
                    return [];
                });
            });

            // await this chunk, then append results and update UI progressively
            const pageResults = await Promise.all(promises);
            pageResults.forEach(arr => all.push(...arr));

            // progressive UI update: give user more rows as they arrive
            if (typeof onPartial === 'function') onPartial(all, { partial: true });
            // continue next chunk
        }

        return all;
    }


    // --- ЗАМЕНИТЬ НА ЭТО: прогрессивная подгрузка и рендер по страницам ---
    try {
        tbody.innerHTML = `<tr><td colspan="7" class="small-muted">Загрузка...</td></tr>`;

        const API_ROOT = '/api/v1/medic/legacy-users/';
        const PAGE_SIZE = 1000; // можно уменьшить/увеличить

        // callback для частичного обновления UI
        function onPartialUpdate(currentAll) {
            // обновляем фильтры и таблицу уже с тем, что пришло
            try { buildFilters(currentAll); } catch(_) {}
            tableFromData(filterData(currentAll));
        }

        // последовательно подтягиваем страницы и вызываем onPartialUpdate после каждой
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
                // добавляем и обновляем UI
                all.push(...results);
                onPartialUpdate(all);

                // следующий url (DRF отдаёт абсолютный next или null)
                url = json.next || null;

                // небольшой yield, чтобы не блокировать UI (даёт браузеру шанс перерисовать)
                await new Promise(res => setTimeout(res, 0));
            }
            return all;
        }

        // запускаем прогрессивный fetch
        const allItems = await fetchAllProgressive();

        // финальный рендер (на случай, если что-то изменилось)
        buildFilters(allItems);
        tableFromData(filterData(allItems));

        // бинды (работают с allItems)
        if (btnRefresh) btnRefresh.addEventListener('click', () => tableFromData(filterData(allItems)));
        if (searchInput) searchInput.addEventListener('input', () => tableFromData(filterData(allItems)));
        if (filterBlood) filterBlood.addEventListener('change', () => tableFromData(filterData(allItems)));
        if (filterCity) filterCity.addEventListener('change', () => tableFromData(filterData(allItems)));

        if (btnExportCsv) btnExportCsv.addEventListener('click', () => {
            const shown = filterData(allItems);
            exportCsv(shown, 'medic_users.csv');
        });
        if (btnExportXls) btnExportXls.addEventListener('click', () => {
            const shown = filterData(allItems);
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


