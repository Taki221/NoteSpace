const buttons = document.querySelectorAll(".new-note");
const emptyState = document.querySelector(".empty-state");
const emptyTitle = document.querySelector(".empty-title");
const emptyDescription = document.querySelector(".empty-description");
const noteEditor = document.querySelector(".note-editor");
const titleInput = document.querySelector(".note-title");
const textInput = document.querySelector(".note-text");
const saveButton = document.querySelector(".save-note");
const notesList = document.querySelector(".notes-list");
const notesListTitle = document.querySelector(".notes-list-title");
const favoriteButton = document.querySelector(".favorite-note");
const deleteButton = document.querySelector(".delete-note");
const restoreButton = document.querySelector(".restore-note");
const deleteForeverButton = document.querySelector(".delete-forever");
const allNotesNav = document.querySelector(".all-notes-nav");
const favoritesNav = document.querySelector(".favorites-nav");
const trashNav = document.querySelector(".trash-nav");
const profileMore = document.querySelector(".profile-more");
const profileMenu = document.querySelector(".profile-menu");
const notesApp = document.querySelector(".notes-app");
const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.querySelector(".sidebar-toggle");
let selectedNote = null;
let selectedCard = null;
let currentView = "all";
let isCreating = false;
const notes = [];
function updateNavigation() {
  allNotesNav.classList.toggle("active", currentView === "all");
  favoritesNav.classList.toggle("active", currentView === "favorites");
  trashNav.classList.toggle("active", currentView === "trash");
}
function openNote(note, card) {
  selectedNote = note;
  selectedCard = card;
  isCreating = false;
  titleInput.value = note.title;
  textInput.value = note.content;
  titleInput.readOnly = note.isDeleted;
  textInput.readOnly = note.isDeleted;
  favoriteButton.classList.toggle("is-active", note.isFavorite);
  favoriteButton.setAttribute("aria-pressed", String(note.isFavorite));
  favoriteButton.classList.toggle("hidden", note.isDeleted);
  deleteButton.classList.toggle("hidden", note.isDeleted);
  saveButton.classList.toggle("hidden", note.isDeleted);
  restoreButton.classList.toggle("hidden", !note.isDeleted);
  deleteForeverButton.classList.toggle("hidden", !note.isDeleted);
  notesList.querySelectorAll(".note-card").forEach(function (item) {
    item.classList.toggle("is-selected", item === card);
  });
  emptyState.classList.add("hidden");
  noteEditor.classList.remove("hidden");
}
function renderNotes() {
  notesList.querySelectorAll(".note-card").forEach(function (card) {
    card.remove();
  });
  const visibleNotes = notes.filter(function (note) {
    if (currentView === "favorites") {
      return note.isFavorite && !note.isDeleted;
    }
    if (currentView === "trash") {
      return note.isDeleted;
    }
    return !note.isDeleted;
  });
  if (currentView === "favorites") {
    notesListTitle.textContent = "Избранное";
  } else if (currentView === "trash") {
    notesListTitle.textContent = "Корзина";
  } else {
    notesListTitle.textContent = "Заметки";
  }
  if (!isCreating && !visibleNotes.includes(selectedNote)) {
    selectedNote = visibleNotes[0] || null;
  }
  selectedCard = null;
  visibleNotes.forEach(function (note) {
    const card = document.createElement("div");
    card.textContent = note.title;
    card.classList.add("note-card");
    card.classList.toggle("is-favorite", note.isFavorite);
    notesList.append(card);
    card.addEventListener("click", function () {
      openNote(note, card);
    });
    if (selectedNote === note) {
      selectedCard = card;
    }
  });
  if (visibleNotes.length === 0 && !isCreating) {
    selectedNote = null;
    emptyTitle.textContent =
      currentView === "favorites"
        ? "В избранном пока нет заметок"
        : currentView === "trash"
          ? "Корзина пуста"
          : "У вас пока нет заметок";
    emptyDescription.textContent =
      currentView === "favorites"
        ? "Отмечайте заметки звёздочкой, чтобы видеть их здесь"
        : currentView === "trash"
          ? "Удалённые заметки будут находиться здесь"
          : "Создайте первую заметку, чтобы начать работу";
    emptyState.classList.remove("hidden");
    noteEditor.classList.add("hidden");
    return;
  }
  emptyState.classList.add("hidden");
  if (isCreating) {
    noteEditor.classList.remove("hidden");
    return;
  }
  if (selectedNote !== null) {
    openNote(selectedNote, selectedCard);
  }
}
buttons.forEach(function (button) {
  button.addEventListener("click", function (event) {
    event.preventDefault();
    currentView = "all";
    isCreating = true;
    selectedNote = null;
    selectedCard = null;
    titleInput.value = "";
    textInput.value = "";
    titleInput.readOnly = false;
    textInput.readOnly = false;
    favoriteButton.classList.remove("is-active");
    favoriteButton.setAttribute("aria-pressed", "false");
    favoriteButton.classList.add("hidden");
    deleteButton.classList.add("hidden");
    restoreButton.classList.add("hidden");
    deleteForeverButton.classList.add("hidden");
    saveButton.classList.remove("hidden");
    updateNavigation();
    renderNotes();
    titleInput.focus();
  });
});
profileMore.addEventListener("click", function () {
  profileMenu.classList.toggle("hidden");
  profileMore.setAttribute(
    "aria-expanded",
    String(!profileMenu.classList.contains("hidden")),
  );
});
document.addEventListener("click", function (event) {
  if (!event.target.closest(".profile")) {
    profileMenu.classList.add("hidden");
    profileMore.setAttribute("aria-expanded", "false");
  }
});
saveButton.addEventListener("click", function () {
  if (selectedNote === null) {
    const newNote = {
      title: titleInput.value.trim() || "Без названия",
      content: textInput.value,
      isFavorite: false,
      isDeleted: false,
    };
    notes.push(newNote);
    selectedNote = newNote;
  } else {
    selectedNote.title = titleInput.value.trim() || "Без названия";
    selectedNote.content = textInput.value;
  }
  isCreating = false;
  renderNotes();
});
favoriteButton.addEventListener("click", function () {
  if (selectedNote === null || selectedNote.isDeleted) {
    return;
  }
  selectedNote.title = titleInput.value.trim() || "Без названия";
  selectedNote.content = textInput.value;
  selectedNote.isFavorite = !selectedNote.isFavorite;
  renderNotes();
});

deleteButton.addEventListener("click", function () {
  if (selectedNote === null || selectedNote.isDeleted) {
    return;
  }
  selectedNote.isDeleted = true;
  selectedNote = null;
  renderNotes();
});
restoreButton.addEventListener("click", function () {
  if (selectedNote === null || !selectedNote.isDeleted) {
    return;
  }
  selectedNote.isDeleted = false;
  currentView = "all";
  updateNavigation();
  renderNotes();
});
deleteForeverButton.addEventListener("click", function () {
  if (selectedNote === null || !selectedNote.isDeleted) {
    return;
  }
  if (!window.confirm("Удалить заметку навсегда?")) {
    return;
  }
  const index = notes.indexOf(selectedNote);
  if (index !== -1) {
    notes.splice(index, 1);
  }
  selectedNote = null;
  renderNotes();
});
allNotesNav.addEventListener("click", function (event) {
  event.preventDefault();
  currentView = "all";
  isCreating = false;
  selectedNote = null;
  updateNavigation();
  renderNotes();
});
favoritesNav.addEventListener("click", function (event) {
  event.preventDefault();
  currentView = "favorites";
  isCreating = false;
  selectedNote = null;
  updateNavigation();
  renderNotes();
});
trashNav.addEventListener("click", function (event) {
  event.preventDefault();
  currentView = "trash";
  isCreating = false;
  selectedNote = null;
  updateNavigation();
  renderNotes();
});
sidebarToggle.addEventListener("click", function () {
  notesApp.classList.toggle("is-collapsed");
  const isCollapsed = notesApp.classList.contains("is-collapsed");
  sidebar.inert = isCollapsed;
  sidebarToggle.setAttribute("aria-expanded", String(!isCollapsed));
  sidebarToggle.setAttribute(
    "aria-label",
    isCollapsed ? "Развернуть меню" : "Свернуть меню",
  );
});
updateNavigation();
renderNotes();
