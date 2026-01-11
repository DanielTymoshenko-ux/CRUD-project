const API = "https://todo-crud-project.up.railway.app/todos";

let tasksCache = [];
let currentFilter = "all";

function escapeHtml(s) {
  if (s == null) return "";
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

async function loadTasks() {
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`Błąd ładowania: ${res.status}`);
    const tasks = await res.json();
    tasksCache = tasks;
    renderTasks();
  } catch (err) {
    console.error(err);
    alert("Nie udało się załadować zadań.");
  }
}

function renderTasks() {
  let filtered = tasksCache;

  if (currentFilter === "active") filtered = tasksCache.filter(t => !t.done);
  else if (currentFilter === "done") filtered = tasksCache.filter(t => t.done);

  filtered = filtered.slice().sort((a, b) => {
    if ((b.priority || 0) === (a.priority || 0)) {
      return new Date(b.created_at) - new Date(a.created_at);
    }
    return (b.priority || 0) - (a.priority || 0);
  });

  const list = document.getElementById("tasks");
  const empty = document.getElementById("emptyState");
  const countEl = document.getElementById("taskCount");

  list.innerHTML = "";
  countEl.textContent = `(${filtered.length} / ${tasksCache.length})`;

  if (filtered.length === 0) {
    empty.style.display = "block";
    return;
  }
  empty.style.display = "none";

  filtered.forEach(t => {
    const li = document.createElement("li");
    li.className = "task";

    const titleCls = "task-title" + (t.done ? " done" : "");
    const prioClass = `chip chip-prio-${t.priority || 3}`;

    li.innerHTML = `
      <div class="task-header">
        <div class="${titleCls}">${escapeHtml(t.title)}</div>
        <div class="${t.done ? "badge-done" : "badge-pending"}">
          ${t.done ? "Ukończone ✅" : "W toku ⏳"}
        </div>
      </div>
      <div class="task-meta">
        ${t.description ? `<span>${escapeHtml(t.description)}</span>` : ""}
        <span class="${prioClass}">Priorytet: ${t.priority ?? "-"}</span>
        <span class="chip">Deadline: ${t.deadline || "-"}</span>
        <span class="chip">Utworzone: ${formatDateTime(t.created_at)}</span>
      </div>
      <div class="task-actions">
        <button class="btn-secondary" onclick="toggleDone(${t.id})">
          ${t.done ? "↩ Oznacz jako w toku" : "✅ Oznacz jako ukończone"}
        </button>
        <button class="btn-secondary" onclick="editTask(${t.id})">✏ Edytuj</button>
        <button class="btn-danger" onclick="deleteTask(${t.id})">🗑 Usuń</button>
      </div>
    `;

    list.appendChild(li);
  });
}

function formatDateTime(iso) {
  if (!iso) return "-";
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

async function saveTask() {
  const id = document.getElementById("taskId").value;
  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const priorityVal = document.getElementById("priority").value;
  const deadline = document.getElementById("deadline").value || null;
  const done = document.getElementById("done").checked;

  if (!title) {
    alert("Tytuł jest wymagany");
    return;
  }

  const priority = priorityVal ? parseInt(priorityVal, 10) : 3;
  if (priority < 1 || priority > 5) {
    alert("Priorytet musi być między 1 a 5");
    return;
  }

  const payload = { title, description, priority, deadline, done };

  let url = API;
  let method = "POST";

  if (id) {
    url = `${API}/${id}`;
    method = "PUT";
  }

  try {
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      alert("Błąd: " + (err.error || res.status));
      return;
    }

    clearForm();
    loadTasks();
  } catch (err) {
    console.error(err);
    alert("Nie udało się zapisać zadania.");
  }
}

function clearForm() {
  document.getElementById("taskId").value = "";
  document.getElementById("title").value = "";
  document.getElementById("description").value = "";
  document.getElementById("priority").value = 3;
  document.getElementById("deadline").value = "";
  document.getElementById("done").checked = false;
}

async function deleteTask(id) {
  if (!confirm("Na pewno chcesz usunąć to zadanie?")) return;

  try {
    const res = await fetch(`${API}/${id}`, { method: "DELETE" });
    if (!res.ok) alert("Nie udało się usunąć zadania.");
    loadTasks();
  } catch (err) {
    console.error(err);
    alert("Błąd sieci przy usuwaniu zadania.");
  }
}

function editTask(id) {
  const t = tasksCache.find(x => x.id === id);
  if (!t) return;

  document.getElementById("taskId").value = t.id;
  document.getElementById("title").value = t.title || "";
  document.getElementById("description").value = t.description || "";
  document.getElementById("priority").value = t.priority || 3;
  document.getElementById("deadline").value = t.deadline || "";
  document.getElementById("done").checked = !!t.done;
  document.getElementById("title").focus();
}

async function toggleDone(id) {
  const t = tasksCache.find(x => x.id === id);
  if (!t) return;

  try {
    const res = await fetch(`${API}/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ done: !t.done })
    });

    if (!res.ok) alert("Nie udało się zmienić statusu");
    loadTasks();
  } catch (err) {
    console.error(err);
    alert("Błąd sieci przy zmianie statusu");
  }
}

function setFilter(filter) {
  currentFilter = filter;
  document.getElementById("filter-all").classList.remove("active");
  document.getElementById("filter-active").classList.remove("active");
  document.getElementById("filter-done").classList.remove("active");

  if (filter === "all") document.getElementById("filter-all").classList.add("active");
  else if (filter === "active") document.getElementById("filter-active").classList.add("active");
  else if (filter === "done") document.getElementById("filter-done").classList.add("active");

  renderTasks();
}

window.addEventListener("load", loadTasks);
