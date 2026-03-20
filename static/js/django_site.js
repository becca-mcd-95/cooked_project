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
    const stars = "*".repeat(full) + ".".repeat(5 - full);
    el.textContent = `${stars} `;
    const muted = document.createElement("span");
    muted.className = "muted";
    muted.textContent = `${rating.toFixed(1)}`;
    el.appendChild(muted);
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
        renderAllStars(container);
        form.reset();
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
        const res = await postJson(`/cooked/review/${reviewId}/delete/`, {});
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
    const submit = document.querySelector("[data-ingredient-submit]");
    const results = document.getElementById("filterResults");
    const countEl = document.getElementById("resultCount");
    if (!root || !submit || !results) return;

    const getMode = () => {
      const checked = document.querySelector('input[name="mode"]:checked');
      return checked ? checked.value : "strict";
    };

    const getIds = () => {
      return Array.from(root.querySelectorAll('input[type="checkbox"]:checked')).map((x) => x.value);
    };

    const run = async () => {
      const ids = getIds();
      const mode = getMode();
      const url = `/cooked/ingredients/filter/?ingredients=${encodeURIComponent(ids.join(","))}&mode=${encodeURIComponent(mode)}`;
      const res = await fetch(url, { headers: { "Accept": "application/json" } });
      const data = await res.json();
      results.innerHTML = data.html || "";
      if (countEl) countEl.textContent = String(data.count || 0);
      renderAllStars(results);
    };

    submit.addEventListener("click", run);
  }

  function setupFollowToggle() {
    document.addEventListener("click", async (e) => {
      const btn = e.target instanceof Element ? e.target.closest("[data-follow-toggle]") : null;
      if (!btn) return;
      const username = btn.getAttribute("data-username");
      if (!username) return;
      try {
        const res = await postJson(`/cooked/follow/${encodeURIComponent(username)}/toggle/`, {});
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
        const res = await postJson(`/cooked/recipes/${recipeId}/status/toggle/`, { status });
        if (status === "wishlist") {
          btn.classList.toggle("btn--primary", !res.wishlist);
          btn.classList.toggle("btn--ghost", !!res.wishlist);
          btn.textContent = res.wishlist ? "In wishlist (remove)" : "Add to wishlist";
        } else if (status === "cooked") {
          btn.textContent = res.cooked ? "Cooked (undo)" : "Mark as cooked";
        }
      } catch (err) {
        alert(err.message || "Failed to toggle status.");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderAllStars(document);
    setupReviewAjax();
    setupIngredientSearch();
    setupFollowToggle();
    setupStatusToggle();
  });
})();
