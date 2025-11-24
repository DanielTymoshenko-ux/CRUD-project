const API_URL = "";

function showTaskErrors(errors) {
  const el = document.getElementById("taskErrors");
  if (!errors || !errors.length) {
    el.style.display = "none";
    el.textContent = "";
    return;
  }
  el.style.display = "block";
  el.innerHTML = errors.map(e => `<div>${e.field}: ${e.message}</div>`).join("");
}

async function loadTasks() {
  const res = await fetch(`/tasks`);
  return await res.json();
}

async function addTask() {
  const titleEl = document.getElementById("title");
  const categoryEl = document.getElementById("category");
  const priorityEl = document.getElementById("priority");
  const deadlineEl = document.getElementById("deadline");

  const errors = [];
  const title = titleEl.value.trim();
  if (title.length < 3 || title.length > 50) errors.push({ field: "title", message: "Title must be 3-50 chars" });

  const category = categoryEl.value.trim();
  if (category && category.length > 50) errors.push({ field: "category", message: "Category max 50 chars" });

  const priority = parseInt(priorityEl.value || "0", 10);
  if (Number.isNaN(priority)  priority < 1  priority > 5) errors.push({ field: "priority", message: "Priority 1-5" });

  const deadline = deadlineEl.value;
  if (deadline) {
    const d = new Date(deadline + "T00:00:00");
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (d < today) errors.push({ field: "deadline", message: "Deadline cannot be in the past" });
  }

  if (errors.length) {
    showTaskErrors(errors);
    return;
  }
  showTaskErrors(null);

  const payload = { title, category, priority, deadline: deadline || null };
  const res = await fetch("/add_task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    location.reload();
    return;
  }

  let json;
  try { json = await res.json(); } catch (e) { alert("Request failed"); return; }
  if (json.fieldErrors) {
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
    const json = await res.json().catch(() => null);
    alert((json && json.error) ? json.error : "Delete failed");
  }
}

async function updateTask(id) {
  const title = prompt("New title:");
  if (title === null) return;
  const category = prompt("New category:");
  const priority = prompt("New priority (1-5):");
  const deadline = prompt("New deadline (YYYY-MM-DD):");

  const res = await fetch(`/update_task/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, category, priority, deadline })
  });

  if (res.ok) location.reload();
  else {
    const json = await res.json().catch(() => null);
    if (json && json.fieldErrors) {
      showTaskErrors(json.fieldErrors);
    } else {
      alert("Update failed");
    }
  }
}

async function fetchWeather() {
  const city = document.getElementById("cityInput").value.trim();
  const loading = document.getElementById("weatherLoading");
  const err = document.getElementById("weatherError");
  const result = document.getElementById("weatherResult");
  const list = document.getElementById("weatherList");

  err.style.display = "none";
  result.style.display = "none";
  list.innerHTML = "";
  loading.style.display = "block";

  try {
    if (!city) throw new Error("City is required");

    const url = ${window.location.origin}/external/weather?city=${encodeURIComponent(city)};
    const res = await fetch(url);

    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      throw new Error(`Server returned non-JSON: ${res.status}`);
    }

    const j = await res.json();
    if (!res.ok) {
      throw new Error(`${j.error || "Error"} Error ${res.status}`);
    }

    (j.forecast || []).forEach(item => {
      const d = document.createElement("div");
      d.textContent = ${item.time} — ${item.temperature} °C;
      list.appendChild(d);
    });

    result.style.display = "block";
  } catch (e) {
    err.textContent = "Błąd: " + e.message;
    err.style.display = "block";
  } finally {
    loading.style.display = "none";
  }
}

async function fetchRates() {
  const base = document.getElementById("baseSel").value;
  const symbols = document.getElementById("symbolsInput").value;
  const loading = document.getElementById("ratesLoading");
  const err = document.getElementById("ratesError");
  const table = document.getElementById("ratesTable");
  const body = document.getElementById("ratesBody");

  err.style.display = "none";
  table.style.display = "none";
  body.innerHTML = "";
  loading.style.display = "block";

  try {
    const params = new URLSearchParams();
    params.set("base", base);
    if (symbols) params.set("symbols", symbols);

    const url = ${window.location.origin}/external/rates?${params.toString()};
    const res = await fetch(url);

    const ct = res.headers.get("content-type") || "";
    if (!ct.includes("application/json")) {
      throw new Error(`Server returned non-JSON: ${res.status}`);
    }

    const j = await res.json();
    if (!res.ok) {
      throw new Error(`${j.error || "Error"} Error ${res.status}`);
    }

    (j.rates || []).forEach(item => {
      const tr = document.createElement("tr");
      const td1 = document.createElement("td");
      td1.textContent = item.currency;
      const td2 = document.createElement("td");
      td2.textContent = item.value;
      tr.appendChild(td1);
      tr.appendChild(td2);
      body.appendChild(tr);
    });

    table.style.display = "table";
  } catch (e) {
    err.textContent = "Błąd: " + e.message;
    err.style.display = "block";
  } finally {
    loading.style.display = "none";
  }
}

window.addEventListener("load", () => {
  const btn = document.getElementById("addBtn");
  if (btn) btn.addEventListener("click", addTask);

  const wb = document.getElementById("fetchWeatherBtn");
  if (wb) wb.addEventListener("click", fetchWeather);

  const rb = document.getElementById("fetchRatesBtn");
  if (rb) rb.addEventListener("click", fetchRates);
});
