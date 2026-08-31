(() => {
  const root = document.documentElement;
  const storageKey = "spork-theme";
  const preference = window.matchMedia("(prefers-color-scheme: dark)");
  const colors = { light: "#f2eee4", dark: "#111510" };

  const savedTheme = () => {
    try {
      const value = window.localStorage.getItem(storageKey);
      return value === "light" || value === "dark" ? value : null;
    } catch (_error) {
      return null;
    }
  };

  const currentTheme = () =>
    root.dataset.theme || (preference.matches ? "dark" : "light");

  const updateChrome = () => {
    const color = document.getElementById("theme-color");
    if (color) color.content = colors[currentTheme()];
  };

  const selected = savedTheme();
  if (selected) root.dataset.theme = selected;
  root.classList.add("has-theme-control");
  updateChrome();

  document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("[data-theme-toggle]");
    if (!button) return;

    const renderButton = () => {
      const next = currentTheme() === "dark" ? "light" : "dark";
      button.textContent = next;
      button.setAttribute("aria-label", `Use ${next} theme`);
    };

    button.addEventListener("click", () => {
      const next = currentTheme() === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      try {
        window.localStorage.setItem(storageKey, next);
      } catch (_error) {
        // The selected theme still applies for this page view.
      }
      updateChrome();
      renderButton();
    });

    preference.addEventListener("change", () => {
      if (!root.dataset.theme) {
        updateChrome();
        renderButton();
      }
    });

    renderButton();
  });
})();
