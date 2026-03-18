(function () {
  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  function csrfHeaders() {
    const token = getCookie("csrftoken");
    return token ? { "X-CSRFToken": token } : {};
  }

  function renderStarsEl(el) {
    const raw = el.getAttribute("data-stars");
    const rating = raw ? Number(raw) : 0;
    const full = Math.max(0, Math.min(5, Math.floor(rating)));
    const stars = "★".repeat(full) + "☆".repeat(5 - full);
    el.textContent = `${stars} `;
    const muted = document.createElement("span");
    muted.className = "muted";
    muted.textContent = `${rating.toFixed(1)}`;
    el.appendChild(muted);
  }

  function renderHatsEl(el) {
    const raw = el.getAttribute("data-hats");
    const rating = raw ? Number(raw) : 0;
    const full = Math.max(0, Math.min(5, Math.floor(rating)));
    el.innerHTML = "";
    for (let i = 1; i <= 5; i++) {
      const hat = document.createElement("span");
      hat.className = `chef-hat ${i <= full ? "chef-hat--on" : ""}`.trim();
      hat.setAttribute("aria-hidden", "true");
      el.appendChild(hat);
    }
  }

  function renderAllHats(root) {
    (root || document).querySelectorAll("[data-hats]").forEach(renderHatsEl);
  }

  function renderAllStars(root) {
    (root || document).querySelectorAll(".stars[data-stars]").forEach(renderStarsEl);
  }

  async function postJson(url, formDataOrParams) {
    const body = formDataOrParams instanceof FormData ? formDataOrParams : new URLSearchParams(formDataOrParams);
    const res = await fetch(url, {
      method: "POST",
      headers: { ...csrfHeaders() },
      body,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = data && (data.error || data.detail);
      throw new Error(err || `Request failed (${res.status})`);
    }
    return data;
  }

  function setupReviewAjax() {
    const form = document.getElementById("reviewForm");
    const container = document.getElementById("reviews");
    if (!form || !container) return;

    const errorEl = document.getElementById("reviewError");
    const avgEl = document.getElementById("avgStars");
    const countEl = document.getElementById("reviewCount");
    const hatsEl = document.getElementById("avgHats");
    const modal = document.getElementById("reviewModal");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (errorEl) errorEl.style.display = "none";

      const data = new FormData(form);
      try {
        const res = await postJson(form.action, data);
        if (!res.ok) throw new Error("Failed to save review.");

        const temp = document.createElement("div");
        temp.innerHTML = res.html || "";
        const newNode = temp.firstElementChild;
        if (newNode) {
          const existing = container.querySelector(`[data-review-id="${res.review_id}"]`);
          if (existing) {
            existing.replaceWith(newNode);
          } else {
            container.prepend(newNode);
            if (countEl) countEl.textContent = String(Number(countEl.textContent || "0") + 1);
          }
        }

        if (avgEl && typeof res.avg_rating !== "undefined") {
          avgEl.setAttribute("data-stars", String(res.avg_rating));
          renderStarsEl(avgEl);
        }
        if (hatsEl && typeof res.avg_rating !== "undefined") {
          hatsEl.setAttribute("data-hats", String(res.avg_rating));
          renderHatsEl(hatsEl);
        }
        renderAllStars(container);
        renderAllHats(document);
        form.reset();
        if (modal && modal instanceof HTMLDialogElement && modal.open) modal.close();
      } catch (err) {
        if (errorEl) {
          errorEl.textContent = err.message || "Failed to submit review.";
          errorEl.style.display = "block";
        }
      }
    });

    container.addEventListener("click", async (e) => {
      const btn = e.target instanceof Element ? e.target.closest("[data-review-delete]") : null;
      if (!btn) return;
      const reviewId = btn.getAttribute("data-review-id");
      if (!reviewId) return;

      try {
        const res = await postJson(`/reviews/${reviewId}/delete/`, {});
        const node = container.querySelector(`[data-review-id="${reviewId}"]`);
        if (node) node.remove();
        if (countEl) countEl.textContent = String(Math.max(0, Number(countEl.textContent || "0") - 1));
        if (avgEl && typeof res.avg_rating !== "undefined") {
          avgEl.setAttribute("data-stars", String(res.avg_rating));
          renderStarsEl(avgEl);
        }
      } catch (err) {
        alert(err.message || "Failed to delete review.");
      }
    });
  }

  function setupIngredientSearch() {
    const root = document.querySelector("[data-ingredient-search]");
    const filters = document.querySelector("[data-ingredient-filters]");
    const submit = document.querySelector("[data-ingredient-submit]");
    const results = document.getElementById("filterResults");
    const countEl = document.getElementById("resultCount");
    if (!root || !submit || !results) return;

    const selected = document.querySelector("[data-selected-ingredients]");
    const caption = document.querySelector("[data-results-caption]");
    const filterInput = root.querySelector("[data-filter-input]");
    const filterList = root.querySelector("[data-filter-list]");

    let hasRun = false;

    const getMode = () => {
      const checked = document.querySelector('input[name="mode"]:checked');
      return checked ? checked.value : "strict";
    };

    const getIds = () => {
      return Array.from(root.querySelectorAll('input[type="checkbox"]:checked')).map((x) => x.value);
    };

    const getFilterValues = (name) => {
      if (!filters) return [];
      return Array.from(filters.querySelectorAll(`input[name="${CSS.escape(name)}"]:checked`)).map((x) => x.value);
    };

    const updateSelected = () => {
      if (!selected) return;
      selected.innerHTML = "";
      const checks = Array.from(root.querySelectorAll('input[type="checkbox"]:checked'));
      const names = [];
      if (!checks.length) {
        const empty = document.createElement("span");
        empty.className = "chip chip--muted";
        empty.textContent = "No ingredients selected";
        selected.appendChild(empty);
        if (caption) caption.textContent = "Showing best matches";
        return;
      }

      checks.forEach((box) => {
        const label = box.closest("label");
        const nameEl = label ? label.querySelector("span") : null;
        const name = (nameEl ? nameEl.textContent : "") || box.value;
        names.push(name.trim());
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip";
        chip.textContent = name.trim();
        chip.setAttribute("data-ingredient-id", box.value);
        selected.appendChild(chip);
      });

      if (caption) {
        const quoted = names.map((x) => `"${x}"`).join(" ");
        caption.textContent = quoted ? `Showing best matches for ${quoted}` : "Showing best matches";
      }
    };

    const run = async () => {
      const ids = getIds();
      const mode = getMode();
      const params = new URLSearchParams();
      params.set("ingredients", ids.join(","));
      params.set("mode", mode);

      getFilterValues("country").forEach((v) => params.append("country", v));
      getFilterValues("cuisine").forEach((v) => params.append("cuisine", v));
      getFilterValues("difficulty").forEach((v) => params.append("difficulty", v));
      getFilterValues("occasion").forEach((v) => params.append("occasion", v));

      const url = `/social/ingredients/filter/?${params.toString()}`;
      const res = await fetch(url, { headers: { "Accept": "application/json" } });
      const data = await res.json();
      results.innerHTML = data.html || "";
      if (countEl) countEl.textContent = String(data.count || 0);
      renderAllStars(results);
      hasRun = true;
    };

    submit.addEventListener("click", run);
    root.addEventListener("change", updateSelected);
    const modeRadios = document.querySelectorAll('input[name="mode"]');
    modeRadios.forEach((r) => r.addEventListener("change", () => (hasRun || getIds().length ? run() : undefined)));
    if (filters) {
      filters.addEventListener("change", () => (hasRun || getIds().length ? run() : undefined));
    }
    if (filterInput && filterList) {
      const applyListFilter = () => {
        const q = (filterInput.value || "").trim().toLowerCase();
        filterList.querySelectorAll("[data-filter-item]").forEach((item) => {
          const hay = (item.textContent || "").toLowerCase();
          item.style.display = !q || hay.includes(q) ? "" : "none";
        });
      };
      filterInput.addEventListener("input", applyListFilter);
      filterInput.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
          filterInput.value = "";
          applyListFilter();
        }
      });
      applyListFilter();
    }
    if (selected) {
      selected.addEventListener("click", (e) => {
        const btn = e.target instanceof Element ? e.target.closest("[data-ingredient-id]") : null;
        if (!btn) return;
        const id = btn.getAttribute("data-ingredient-id");
        if (!id) return;
        const box = root.querySelector(`input[type="checkbox"][value="${CSS.escape(id)}"]`);
        if (box) box.checked = false;
        updateSelected();
      });
    }
    updateSelected();
  }

  function setupRatingPickers() {
    document.querySelectorAll("[data-rating-picker]").forEach((root) => {
      if (!(root instanceof Element)) return;
      const hidden = root.querySelector("[data-rating-value]");
      const buttons = Array.from(root.querySelectorAll("[data-rate]"));
      if (!(hidden instanceof HTMLInputElement) || !buttons.length) return;

      const set = (val) => {
        const n = Number(val) || 0;
        hidden.value = String(n);
        buttons.forEach((btn) => {
          const r = Number(btn.getAttribute("data-rate") || "0");
          btn.classList.toggle("chef-hat--on", r <= n);
        });
      };

      root.addEventListener("click", (e) => {
        const btn = e.target instanceof Element ? e.target.closest("[data-rate]") : null;
        if (!btn) return;
        const val = btn.getAttribute("data-rate") || "0";
        set(val);
      });

      set(hidden.value || "5");
    });
  }

  function setupDialogs() {
    document.addEventListener("click", (e) => {
      const openBtn = e.target instanceof Element ? e.target.closest("[data-dialog-open]") : null;
      if (openBtn) {
        const id = openBtn.getAttribute("data-dialog-open");
        const dialog = id ? document.getElementById(id) : null;
        if (dialog && dialog instanceof HTMLDialogElement) dialog.showModal();
        return;
      }

      const closeBtn = e.target instanceof Element ? e.target.closest("[data-dialog-close]") : null;
      if (closeBtn) {
        const dialog = closeBtn.closest("dialog");
        if (dialog && dialog instanceof HTMLDialogElement) dialog.close();
      }
    });

    document.querySelectorAll("dialog.app-dialog").forEach((dialog) => {
      if (!(dialog instanceof HTMLDialogElement)) return;
      dialog.addEventListener("click", (e) => {
        const rect = dialog.getBoundingClientRect();
        const inDialog =
          rect.top <= e.clientY && e.clientY <= rect.bottom && rect.left <= e.clientX && e.clientX <= rect.right;
        if (!inDialog) dialog.close();
      });
    });

    document.querySelectorAll("dialog[data-open-on-load]").forEach((dialog) => {
      if (dialog instanceof HTMLDialogElement) dialog.showModal();
    });
  }

  function setupProfileEditPreviews() {
    const dialog = document.getElementById("editProfileModal");
    if (!(dialog instanceof HTMLDialogElement)) return;

    const coverInput = dialog.querySelector('input[type="file"][name="cover"]');
    const avatarInput = dialog.querySelector('input[type="file"][name="avatar"]');
    const coverImg = dialog.querySelector("[data-cover-preview]");
    const coverPlaceholder = dialog.querySelector("[data-cover-placeholder]");
    const avatarImg = dialog.querySelector("[data-avatar-preview]");
    const avatarFallback = dialog.querySelector("[data-avatar-fallback]");

    const state = {
      coverUrl: "",
      avatarUrl: "",
      initialCoverSrc: coverImg instanceof HTMLImageElement ? coverImg.getAttribute("src") || "" : "",
      initialAvatarSrc: avatarImg instanceof HTMLImageElement ? avatarImg.getAttribute("src") || "" : "",
    };

    const revoke = (kind) => {
      const key = kind === "cover" ? "coverUrl" : "avatarUrl";
      const url = state[key];
      if (url) URL.revokeObjectURL(url);
      state[key] = "";
    };

    const setImageFromFile = (kind, file) => {
      const img = kind === "cover" ? coverImg : avatarImg;
      const placeholder = kind === "cover" ? coverPlaceholder : avatarFallback;
      if (!(img instanceof HTMLImageElement)) return;

      revoke(kind);
      const url = URL.createObjectURL(file);
      if (kind === "cover") state.coverUrl = url;
      else state.avatarUrl = url;

      img.src = url;
      img.style.display = "";
      if (placeholder instanceof HTMLElement) placeholder.style.display = "none";
    };

    const restoreInitial = (kind) => {
      const img = kind === "cover" ? coverImg : avatarImg;
      const placeholder = kind === "cover" ? coverPlaceholder : avatarFallback;
      const initialSrc = kind === "cover" ? state.initialCoverSrc : state.initialAvatarSrc;

      revoke(kind);

      if (!(img instanceof HTMLImageElement)) return;
      if (initialSrc) {
        img.src = initialSrc;
        img.style.display = "";
        if (placeholder instanceof HTMLElement) placeholder.style.display = "none";
      } else {
        img.removeAttribute("src");
        img.style.display = "none";
        if (placeholder instanceof HTMLElement) placeholder.style.display = "";
      }
    };

    if (coverInput instanceof HTMLInputElement) {
      coverInput.addEventListener("change", () => {
        const file = coverInput.files && coverInput.files[0];
        if (!file) return restoreInitial("cover");
        setImageFromFile("cover", file);
      });
    }

    if (avatarInput instanceof HTMLInputElement) {
      avatarInput.addEventListener("change", () => {
        const file = avatarInput.files && avatarInput.files[0];
        if (!file) return restoreInitial("avatar");
        setImageFromFile("avatar", file);
      });
    }

    dialog.addEventListener("close", () => {
      revoke("cover");
      revoke("avatar");
    });
  }

  function setupRecipeSearchForm() {
    const form = document.querySelector("[data-recipe-search-form]");
    if (!(form instanceof HTMLFormElement)) return;
    const filters = form.querySelector("[data-recipe-search-filters]");
    if (!(filters instanceof Element)) return;

    filters.addEventListener("change", () => {
      form.submit();
    });
  }

  function setupFollowToggle() {
    document.addEventListener("click", async (e) => {
      const btn = e.target instanceof Element ? e.target.closest("[data-follow-toggle]") : null;
      if (!btn) return;
      const username = btn.getAttribute("data-username");
      if (!username) return;
      try {
        const res = await postJson(`/social/follow/${encodeURIComponent(username)}/toggle/`, {});
        if (res.following) {
          btn.classList.remove("btn--primary");
          btn.classList.add("btn--ghost");
          btn.textContent = "Following";
        } else {
          btn.classList.remove("btn--ghost");
          btn.classList.add("btn--primary");
          btn.textContent = "Follow";
        }
      } catch (err) {
        alert(err.message || "Failed to follow/unfollow.");
      }
    });
  }

  function setupStatusToggle() {
    document.addEventListener("click", async (e) => {
      const btn = e.target instanceof Element ? e.target.closest("[data-status-toggle]") : null;
      if (!btn) return;
      const recipeWrap = btn.closest("[data-recipe-id]");
      const recipeId = recipeWrap ? recipeWrap.getAttribute("data-recipe-id") : null;
      const status = btn.getAttribute("data-status");
      if (!recipeId || !status) return;

      try {
        const res = await postJson(`/social/recipes/${recipeId}/status/toggle/`, { status });
        const setPressed = (el, on) => {
          el.setAttribute("aria-pressed", on ? "true" : "false");
          el.classList.toggle("iconbtn--active", !!on);
        };

        if (status === "wishlist") {
          if (btn.classList.contains("iconbtn")) {
            setPressed(btn, !!res.wishlist);
            const count = recipeWrap.querySelector('[data-status-count="wishlist"]');
            if (count) count.textContent = String(res.wishlist_count ?? count.textContent);
            if (recipeWrap.closest("[data-to-cook-section]") && !res.wishlist) recipeWrap.remove();
          } else {
            btn.classList.toggle("btn--primary", !res.wishlist);
            btn.classList.toggle("btn--ghost", !!res.wishlist);
            btn.textContent = res.wishlist ? "In wishlist (remove)" : "Add to wishlist";
          }
        } else if (status === "cooked") {
          if (btn.classList.contains("iconbtn")) {
            setPressed(btn, !!res.cooked);
            const count = recipeWrap.querySelector('[data-status-count="cooked"]');
            if (count) count.textContent = String(res.cooked_count ?? count.textContent);
          } else {
            btn.textContent = res.cooked ? "Cooked (undo)" : "Mark as cooked";
          }
        }
      } catch (err) {
        alert(err.message || "Failed to toggle status.");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderAllHats(document);
    renderAllStars(document);
    setupReviewAjax();
    setupIngredientSearch();
    setupDialogs();
    setupProfileEditPreviews();
    setupRecipeSearchForm();
    setupRatingPickers();
    setupFollowToggle();
    setupStatusToggle();
  });
})();
