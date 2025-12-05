// -----------------------
// 🟥 Переводы
// -----------------------
const translations = {
    kk: {
        title: "Қан тапсыру",
        filter: "Іздеу бойынша сүзгілеу",
    },
    ru: {
        title: "Сдача крови",
        filter: "Фильтр по поиску",
    },
    en: {
        title: "Blood donation",
        filter: "Search filter",
    }
};


// -----------------------
// 🟦 Применение перевода
// -----------------------
function applyDonateTranslations(lang) {

    // Заголовок карточек
    document.querySelectorAll(".donate-card-title")
        .forEach(el => el.textContent = translations[lang].title);

    // Placeholder фильтра
    const filter = document.getElementById("donateSearch");
    if (filter) filter.placeholder = translations[lang].filter;

    // Сохраняем выбранный язык
    localStorage.setItem("site_lang", lang);
}


// -----------------------
// 🟩 Обработчик кнопок языков
// -----------------------
document.querySelectorAll(".lang-link").forEach(btn => {
    btn.addEventListener("click", () => {
        const lang = btn.dataset.lang;

        applyDonateTranslations(lang);

        // Активная кнопка
        document.querySelectorAll(".lang-link")
            .forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
    });
});


// -----------------------
// 🟨 Поиск — работает по Enter
// -----------------------
document.addEventListener("DOMContentLoaded", () => {
    const searchInput = document.getElementById("donateSearch");

    // Восстановить язык
    let savedLang = localStorage.getItem("site_lang") || "kk";
    applyDonateTranslations(savedLang);

    document.querySelectorAll(".lang-link")
        .forEach(b => b.classList.toggle("active", b.dataset.lang === savedLang));

    // ENTER запускает поиск
    if (searchInput) {
        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                const q = this.value.trim();
                const params = new URLSearchParams(window.location.search);

                if (q) params.set("q", q);
                else params.delete("q");

                window.location.search = params.toString();
            }
        });
    }

 
    searchInput.addEventListener("input", function () {
        const q = this.value.trim();
        const params = new URLSearchParams();

        if (q) params.set("q", q);

        window.location.search = params.toString();
    });
});
