const themeButton = document.querySelector(".theme");
function applyTheme(isDark) {
  document.body.classList.toggle("dark-mode", isDark);
  if (themeButton) {
    const themeIcon = themeButton.querySelector("img");
    if (themeIcon) {
      themeIcon.src = isDark ? "img/icon/sun.svg" : "img/moon.svg";
    }
    themeButton.setAttribute("aria-pressed", String(isDark));
    themeButton.setAttribute(
      "aria-label",
      isDark ? "Включить светлую тему" : "Включить тёмную тему",
    );
  }
}
let savedTheme = "light";
try {
  savedTheme = localStorage.getItem("zametki-theme") || "light";
} catch (error) {
  savedTheme = "light";
}
applyTheme(savedTheme === "dark");
if (themeButton) {
  themeButton.addEventListener("click", function () {
    const isDark = !document.body.classList.contains("dark-mode");
    applyTheme(isDark);
    try {
      localStorage.setItem("zametki-theme", isDark ? "dark" : "light");
    } catch (error) {}
  });
}
const mobileScreen = window.matchMedia("(max-width: 768px)");
const mobileBack = document.querySelector(".mobile-back");
function closeMobileSidebar() {
  notesApp.classList.add("is-collapsed");
  sidebar.inert = true;
  sidebarToggle.setAttribute("aria-expanded", "false");
  sidebarToggle.setAttribute("aria-label", "Развернуть меню");
}
if (mobileScreen.matches) {
  closeMobileSidebar();
}
mobileScreen.addEventListener("change", function (event) {
  if (event.matches) {
    closeMobileSidebar();
  } else {
    notesApp.classList.remove("is-collapsed", "mobile-editor-open");
    sidebar.inert = false;
    sidebarToggle.setAttribute("aria-expanded", "true");
    sidebarToggle.setAttribute("aria-label", "Свернуть меню");
  }
});
mobileBack.addEventListener("click", function () {
  notesApp.classList.remove("mobile-editor-open");
  isCreating = false;
  renderNotes();
});
document.addEventListener("click", function (event) {
  if (!mobileScreen.matches) {
    return;
  }
  if (event.target.closest(".new-note, .note-card")) {
    notesApp.classList.add("mobile-editor-open");
    closeMobileSidebar();
  }
  if (event.target.closest(".all-notes-nav, .favorites-nav, .trash-nav")) {
    notesApp.classList.remove("mobile-editor-open");
    closeMobileSidebar();
  }
  if (event.target.closest(".delete-note, .restore-note")) {
    notesApp.classList.remove("mobile-editor-open");
  }
  if (event.target.closest(".delete-forever") && selectedNote === null) {
    notesApp.classList.remove("mobile-editor-open");
  }
  if (
    event.target.closest(".favorite-note") &&
    noteEditor.classList.contains("hidden")
  ) {
    notesApp.classList.remove("mobile-editor-open");
  }
});
