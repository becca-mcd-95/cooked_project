(function () {
  function setError(root, selector, message) {
    const el = root.querySelector(selector);
    if (!(el instanceof HTMLElement)) return;
    if (!message) {
      el.textContent = "";
      el.style.display = "none";
      return;
    }
    el.textContent = message;
    el.style.display = "";
  }

  function setupSignupValidation() {
    const form = document.querySelector("[data-member1-signup-form]");
    if (!(form instanceof HTMLFormElement)) return;

    form.addEventListener("submit", (e) => {
      const p1 = form.querySelector('input[name="password1"]');
      const p2 = form.querySelector('input[name="password2"]');
      const email = form.querySelector('input[name="email"]');
      const username = form.querySelector('input[name="username"]');
      const p1v = p1 instanceof HTMLInputElement ? p1.value : "";
      const p2v = p2 instanceof HTMLInputElement ? p2.value : "";

      if (email instanceof HTMLInputElement && !email.value.trim()) {
        e.preventDefault();
        setError(form, "[data-member1-signup-error]", "Email is required.");
        email.focus();
        return;
      }
      if (username instanceof HTMLInputElement && !username.value.trim()) {
        e.preventDefault();
        setError(form, "[data-member1-signup-error]", "Username is required.");
        username.focus();
        return;
      }
      if (!p1v || !p2v) {
        e.preventDefault();
        setError(form, "[data-member1-signup-error]", "Password is required.");
        (p1 instanceof HTMLInputElement ? p1 : form).focus();
        return;
      }
      if (p1v !== p2v) {
        e.preventDefault();
        setError(form, "[data-member1-signup-error]", "Passwords do not match.");
        (p2 instanceof HTMLInputElement ? p2 : form).focus();
        return;
      }

      setError(form, "[data-member1-signup-error]", "");
    });
  }

  function setupEditToggle() {
    const toggle = document.querySelector("[data-member1-edit-toggle]");
    const panel = document.querySelector("[data-member1-edit-panel]");
    const cancel = document.querySelector("[data-member1-edit-cancel]");
    if (!(toggle instanceof HTMLElement) || !(panel instanceof HTMLElement)) return;

    const open = () => {
      panel.style.display = "";
      const first = panel.querySelector("input,textarea");
      if (first instanceof HTMLElement) first.focus();
    };
    const close = () => {
      panel.style.display = "none";
      setError(panel, "[data-member1-edit-error]", "");
    };

    toggle.addEventListener("click", () => {
      const showing = panel.style.display !== "none";
      if (showing) close();
      else open();
    });

    if (cancel instanceof HTMLElement) cancel.addEventListener("click", close);
  }

  function setupEditValidation() {
    document.querySelectorAll("[data-member1-edit-form]").forEach((form) => {
      if (!(form instanceof HTMLFormElement)) return;
      form.addEventListener("submit", (e) => {
        const username = form.querySelector('input[name="username"]');
        if (username instanceof HTMLInputElement && !username.value.trim()) {
          e.preventDefault();
          setError(form, "[data-member1-edit-error]", "Username is required.");
          username.focus();
        } else {
          setError(form, "[data-member1-edit-error]", "");
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    setupSignupValidation();
    setupEditToggle();
    setupEditValidation();
  });
})();

