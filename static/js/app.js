function setupFilterPickers() {
  document.querySelectorAll("[data-filter-list]").forEach((list) => {
    const wrapper = list.closest(".ingredient-picker");
    if (!wrapper) return;
    const input = wrapper.querySelector("[data-filter-input]");
    if (!input) return;

    const items = Array.from(list.querySelectorAll("[data-filter-item]"));
    const normalize = (s) => (s || "").toLowerCase().trim();

    input.addEventListener("input", () => {
      const q = normalize(input.value);
      items.forEach((el) => {
        const text = normalize(el.textContent);
        el.style.display = !q || text.includes(q) ? "" : "none";
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupFilterPickers();
  setupDropdowns();
});

function setupDropdowns() {
  const dropdowns = Array.from(document.querySelectorAll("[data-dropdown]"));
  if (!dropdowns.length) return;

  const closeAll = () => {
    dropdowns.forEach((dd) => {
      dd.classList.remove("is-open");
      const btn = dd.querySelector("[data-dropdown-trigger]");
      if (btn) btn.setAttribute("aria-expanded", "false");
    });
  };

  dropdowns.forEach((dd) => {
    const trigger = dd.querySelector("[data-dropdown-trigger]");
    const menu = dd.querySelector("[data-dropdown-menu]");
    if (!trigger || !menu) return;

    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const willOpen = !dd.classList.contains("is-open");
      closeAll();
      if (willOpen) {
        dd.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
      }
    });
  });

  document.addEventListener("click", (e) => {
    const t = e.target;
    if (!(t instanceof Element)) return;
    const inside = t.closest("[data-dropdown]");
    if (!inside) closeAll();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeAll();
  });
}
