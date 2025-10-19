const API_URL = "http://127.0.0.1:5000/api";

async function loadTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  const tasks = await res.json();
  const list = document.getElementById("taskList");
  list.innerHTML = "";
  tasks.forEach(t => {
    const li = document.createElement("li");
    li.innerHTML = `
      <b>${t.title}</b> — ${t.description || ""} 
      [Priority: ${t.priority}] 
      [Deadline: ${t.deadline || "—"}] 
      ${t.done ? "✅" : ""}
      <button onclick="deleteTask(${t.id})">❌</button>
    `;
    list.appendChild(li);
  });
}

async function addTask() {
  const title = document.getElementById("taskTitle").value;
  const description = document.getElementById("taskDesc").value;
  const priority = document.getElementById("taskPriority").value;
  const deadline = document.getElementById("taskDeadline").value;
  if (!title) return alert("Title is required");

  await fetch(`${API_URL}/tasks`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ title, description, priority, deadline })
  });

  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDesc").value = "";
  document.getElementById("taskPriority").value = 3;
  document.getElementById("taskDeadline").value = "";
  loadTasks();
}

async function deleteTask(id) {
  await fetch(`${API_URL}/tasks/${id}`, { method: "DELETE" });
  loadTasks();
}

loadTasks();
