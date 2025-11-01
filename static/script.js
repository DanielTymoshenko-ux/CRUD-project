// Use same origin (relative) so deployment domain works
const API_URL = "";

// helpers
function showTaskErrors(errors){
  const el = document.getElementById("taskErrors");
  if(!errors || !errors.length){
    el.style.display = "none";
    el.textContent = "";
    return;
  }
  el.style.display = "block";
  el.innerHTML = errors.map(e => `<div>${e.field}: ${e.message}</div>`).join("");
}

async function loadTasks() {
    const res = await fetch(`/tasks`);
    // tasks page returns HTML for page; for API tasks list use /tasks (GET) endpoint returning JSON in app.py
    // We'll call the JSON API:
    const api = await fetch(`/tasks`);
    // But we have separate API endpoint /tasks that now returns JSON only if session exists.
    // Using /tasks (GET) for JSON would conflict with HTML route; use /tasks (same) — we already render tasks server-side.
    // For safety, try /tasks (JSON) endpoint /tasks?json=1 could be added, but to keep simple: rely on server-rendered list.
    // Here we don't populate client-side list on page load (server already rendered). Still keep function as minimal.
    return;
}

async function addTask() {
    const titleEl = document.getElementById("title");
    const categoryEl = document.getElementById("category");
    const priorityEl = document.getElementById("priority");
    const deadlineEl = document.getElementById("deadline");

    // client-side validation
    const errors = [];
    const title = titleEl.value.trim();
    if(title.length < 3 || title.length > 50) errors.push({ field: "title", message: "Title must be 3–50 chars" });
    const category = categoryEl.value.trim();
    if(category && category.length > 50) errors.push({ field: "category", message: "Category max 50 chars" });
    const priority = parseInt(priorityEl.value || "0", 10);
    if(Number.isNaN(priority) || priority < 1 || priority > 5) errors.push({ field: "priority", message: "Priority 1–5" });
    const deadline = deadlineEl.value;
    if(deadline){
      const d = new Date(deadline + "T00:00:00");
      const today = new Date();
      today.setHours(0,0,0,0);
      if(d < today) errors.push({ field: "deadline", message: "Deadline cannot be in the past" });
    }

    if(errors.length){
      showTaskErrors(errors);
      return;
    }
    showTaskErrors(null);

    const payload = { title, category, priority, deadline: deadline || null };
    const res = await fetch(`/add_task`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    if(res.ok){
      location.reload();
      return;
    }

    // handle JSON error responses
    let json;
    try { json = await res.json(); } catch(e){ alert("Request failed"); return; }
    if(json.fieldErrors){
      showTaskErrors(json.fieldErrors);
    } else {
      alert(`${json.error || "Error"} (${res.status})`);
    }
}

async function deleteTask(id) {
  if (!confirm("Sure to remove?")) return;
  const res = await fetch(`/delete_task/${id}`, { method: "DELETE" });
  if (res.ok) location.reload();
  else {
    const json = await res.json().catch(()=>null);
    alert((json && json.error) ? json.error : "Delete failed");
  }
}

async function updateTask(id) {
  const title = prompt("New title:");
  if(title === null) return; // cancelled
  const category = prompt("New category:");
  const priority = prompt("New priority (1-5):");
  const deadline = prompt("New deadline (YYYY-MM-DD):");

  const res = await fetch(`/update_task/${id}`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ title, category, priority, deadline })
  });
  if(res.ok) location.reload();
  else {
    const json = await res.json().catch(()=>null);
    if(json && json.fieldErrors){
      showTaskErrors(json.fieldErrors);
    } else {
      alert("Update failed");
    }
  }
}

// attach event
window.addEventListener("load", () => {
  const btn = document.getElementById("addBtn");
  if(btn) btn.addEventListener("click", addTask);
});
