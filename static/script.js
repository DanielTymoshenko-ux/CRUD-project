const API_URL = "http://127.0.0.1:5000/api";

async function loadTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  const tasks = await res.json();
  const list = document.getElementById("taskList");
  list.innerHTML = "";
  tasks.forEach(t => {
    const li = document.createElement("li");
    li.textContent = `${t.title} — ${t.description || ""} ${t.done ? "✅" : ""}`;
    list.appendChild(li);
  });
}

async function addTask() {
  const title = document.getElementById("taskTitle").value;
  const description = document.getElementById("taskDesc").value;
  if (!title) return;
  await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ title, description })
  });
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDesc").value = "";
  loadTasks();
}

loadTasks();
