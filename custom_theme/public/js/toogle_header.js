document.addEventListener("DOMContentLoaded", function () {

  const toggle = (btn, menu) => {
    if (!btn || !menu) return;

    btn.addEventListener("click", () => {
      menu.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
      if (!btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add("hidden");
      }
    });
  };

  toggle(
    document.getElementById("menu-button"),
    document.getElementById("menu-dropdown-mobile")
  );

  toggle(
    document.getElementById("menu-button-desktop"),
    document.getElementById("menu-dropdown-desktop")
  );

});



