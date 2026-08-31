(() => {
  const root = document.documentElement;
  root.classList.add("has-docs-menu");

  document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector("[data-docs-menu-toggle]");
    const panel = document.querySelector("[data-docs-menu-panel]");
    if (!button || !panel) return;

    const mobile = window.matchMedia("(max-width: 48rem)");
    const header = document.querySelector(".site-header");
    let positionFrame = null;

    const updateButtonPosition = () => {
      button.classList.toggle(
        "is-scrolled",
        Boolean(header && header.getBoundingClientRect().bottom <= 0),
      );
      positionFrame = null;
    };

    const requestButtonPositionUpdate = () => {
      if (positionFrame === null) {
        positionFrame = window.requestAnimationFrame(updateButtonPosition);
      }
    };

    window.addEventListener("scroll", requestButtonPositionUpdate, {
      passive: true,
    });
    window.addEventListener("resize", requestButtonPositionUpdate);
    updateButtonPosition();

    const isOpen = () => button.getAttribute("aria-expanded") === "true";

    const setOpen = (open, returnFocus = false) => {
      button.setAttribute("aria-expanded", String(open));
      button.setAttribute(
        "aria-label",
        `${open ? "Close" : "Open"} documentation picker`,
      );
      panel.classList.toggle("is-open", open);
      document.body.classList.toggle("docs-menu-open", open);

      if (open) {
        panel.setAttribute("role", "dialog");
        panel.setAttribute("aria-modal", "true");
        panel.setAttribute("aria-labelledby", "docs-menu-title");
      } else {
        panel.removeAttribute("role");
        panel.removeAttribute("aria-modal");
        panel.removeAttribute("aria-labelledby");
      }

      if (returnFocus) button.focus();
    };

    button.addEventListener("click", () => setOpen(!isOpen()));

    panel.addEventListener("click", (event) => {
      if (mobile.matches && event.target.closest("a")) setOpen(false);
    });

    document.addEventListener("pointerdown", (event) => {
      if (
        isOpen() &&
        !panel.contains(event.target) &&
        !button.contains(event.target)
      ) {
        setOpen(false);
      }
    });

    document.addEventListener("keydown", (event) => {
      if (!isOpen()) return;

      if (event.key === "Escape") {
        setOpen(false, true);
        return;
      }

      if (event.key === "Tab" && mobile.matches) {
        const focusable = [
          button,
          ...panel.querySelectorAll("a, summary"),
        ];
        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    });

    mobile.addEventListener("change", () => setOpen(false));
  });
})();
