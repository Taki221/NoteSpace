// --- Элементы DOM ---
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
const noteDates = document.querySelector(".note-dates");
const noteCreated = document.querySelector(".note-created");
const noteUpdated = document.querySelector(".note-updated");

let notes = [];
let selectedNoteId = null;
let currentView = "all";
let isCreating = false;

const API_URL = "/api";

async function loadNotes() {
  try {

    const response = await fetch(`${API_URL}/notes/`, {
      method: "GET",
      credentials: "include",
    });
    if (!response.ok) throw new Error("Ошибка при загрузке заметок");
    
    const data = await response.json();
    
    notes = data.map(note => ({
      id: note.id,
      title: note.title,
      content: note.content,
      isFavorite: note.is_favorite,
      isDeleted: note.is_deleted,
      createdAt: note.created_at,
      updatedAt: note.updated_at,
    }));
    
    renderNotes();
  } catch (error) {
    console.error(error);
    alert("Не удалось загрузить заметки. Проверьте, запущен ли сервер.");
  }
}

async function saveNoteToServer(title, content) {
  try {
    if (selectedNoteId === null) {

      const response = await fetch(`${API_URL}/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title, content: content }),
        credentials: "include",
      });
      const newNote = await response.json();
      selectedNoteId = newNote.id;
    } else {
      await fetch(`${API_URL}/notes/${selectedNoteId}/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: title, content: content }),
        credentials: "include",
      });
    }
    await loadNotes();
  } catch (error) {
    console.error(error);
  }
}

async function updateNoteField(id, field, value) {
  try {
    await fetch(`${API_URL}/notes/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ [field]: value }),
      credentials: "include",
    });
    await loadNotes();
  } catch (error) {
    console.error(error);
  }
}

async function deleteNoteFromServer(id) {
  try {
    const response = await fetch(`${API_URL}/notes/${id}/`, {
      method: "DELETE",
      credentials: "include",
    });
    
    if (!response.ok) throw new Error("Ошибка при удалении на сервере");
    
    selectedNoteId = null;
    await loadNotes();
  } catch (error) {
    console.error(error);
    alert("Не удалось удалить заметку. Проверьте консоль браузера.");
  }
}


function updateNavigation() {
  allNotesNav.classList.toggle("active", currentView === "all");
  favoritesNav.classList.toggle("active", currentView === "favorites");
  trashNav.classList.toggle("active", currentView === "trash");
}

function formatDate(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function openNote(note, card) {
  selectedNoteId = note.id;
  isCreating = false;
  titleInput.value = note.title;
  textInput.value = note.content;
  titleInput.readOnly = note.isDeleted;
  textInput.readOnly = note.isDeleted;
  noteDates.classList.remove("hidden");
  noteCreated.textContent = `Создано: ${formatDate(note.createdAt)}`;
  if (note.updatedAt) {
    noteUpdated.textContent = `Изменено: ${formatDate(note.updatedAt)}`;
    noteUpdated.classList.remove("hidden");
  } else {
    noteUpdated.classList.add("hidden");
  }
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
    if (currentView === "favorites") return note.isFavorite && !note.isDeleted;
    if (currentView === "trash") return note.isDeleted;
    return !note.isDeleted;
  });

  if (currentView === "favorites") notesListTitle.textContent = "Избранное";
  else if (currentView === "trash") notesListTitle.textContent = "Корзина";
  else notesListTitle.textContent = "Заметки";

  const currentNote = visibleNotes.find(n => n.id === selectedNoteId);
  if (!isCreating && !currentNote) {
    selectedNoteId = visibleNotes[0] ? visibleNotes[0].id : null;
  }

  let selectedCard = null;
  
  visibleNotes.forEach(function (note) {
    const card = document.createElement("div");
    card.textContent = note.title;
    card.classList.add("note-card");
    card.classList.toggle("is-favorite", note.isFavorite);
    notesList.append(card);
    
    card.addEventListener("click", function () {
      openNote(note, card);
    });
    if (selectedNoteId === note.id) {
      selectedCard = card;
    }
  });

  if (visibleNotes.length === 0 && !isCreating) {
    selectedNoteId = null;
    emptyTitle.textContent = currentView === "favorites" ? "В избранном пока нет заметок" : currentView === "trash" ? "Корзина пуста" : "У вас пока нет заметок";
    emptyDescription.textContent = currentView === "favorites" ? "Отмечайте заметки звёздочкой, чтобы видеть их здесь" : currentView === "trash" ? "Удалённые заметки будут находиться здесь" : "Создайте первую заметку, чтобы начать работу";
    emptyState.classList.remove("hidden");
    noteEditor.classList.add("hidden");
    return;
  }

  emptyState.classList.add("hidden");
  if (isCreating) {
    noteEditor.classList.remove("hidden");
    return;
  }
  if (selectedNoteId !== null && currentNote) {
    openNote(currentNote, selectedCard);
  }
}

buttons.forEach(function (button) {
  button.addEventListener("click", function (event) {
    event.preventDefault();
    currentView = "all";
    isCreating = true;
    selectedNoteId = null;
    titleInput.value = "";
    textInput.value = "";
    noteDates.classList.add("hidden");
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
  profileMore.setAttribute("aria-expanded", String(!profileMenu.classList.contains("hidden")));
});

document.addEventListener("click", function (event) {
  if (!event.target.closest(".profile")) {
    profileMenu.classList.add("hidden");
    profileMore.setAttribute("aria-expanded", "false");
  }
});

saveButton.addEventListener("click", async function () {
  const title = titleInput.value.trim() || "Без названия";
  await saveNoteToServer(title, textInput.value);
  isCreating = false;
});

favoriteButton.addEventListener("click", async function () {
  if (selectedNoteId === null) return;
  const currentNote = notes.find(n => n.id === selectedNoteId);
  if (!currentNote || currentNote.isDeleted) return;
  
  const newFavState = !currentNote.isFavorite;
  await updateNoteField(selectedNoteId, "is_favorite", newFavState);
});

deleteButton.addEventListener("click", async function () {
  if (selectedNoteId === null) return;
  await updateNoteField(selectedNoteId, "is_deleted", true);
  selectedNoteId = null;
});

restoreButton.addEventListener("click", async function () {
  if (selectedNoteId === null) return;
  await updateNoteField(selectedNoteId, "is_deleted", false);
  currentView = "all";
  updateNavigation();
});

deleteForeverButton.addEventListener("click", async function () {
  if (selectedNoteId === null) return;
  if (!window.confirm("Удалить заметку навсегда?")) return;
  await deleteNoteFromServer(selectedNoteId);
});

allNotesNav.addEventListener("click", function (event) {
  event.preventDefault(); currentView = "all"; isCreating = false; selectedNoteId = null; updateNavigation(); renderNotes();
});
favoritesNav.addEventListener("click", function (event) {
  event.preventDefault(); currentView = "favorites"; isCreating = false; selectedNoteId = null; updateNavigation(); renderNotes();
});
trashNav.addEventListener("click", function (event) {
  event.preventDefault(); currentView = "trash"; isCreating = false; selectedNoteId = null; updateNavigation(); renderNotes();
});

sidebarToggle.addEventListener("click", function () {
  notesApp.classList.toggle("is-collapsed");
  const isCollapsed = notesApp.classList.contains("is-collapsed");
  sidebar.inert = isCollapsed;
  sidebarToggle.setAttribute("aria-expanded", String(!isCollapsed));
  sidebarToggle.setAttribute("aria-label", isCollapsed ? "Развернуть меню" : "Свернуть меню");
});

updateNavigation();
loadNotes();