const API_URL = '/api'; 


async function loadTasks() {
  const res = await fetch(`${API_URL}/tasks`);
  if (!res.ok) {
    alert('Помилка при завантаженні задач');
    return;
  }
  const tasks = await res.json();
  renderTasks(tasks);
}


async function addTask() {
  const title = document.getElementById('taskTitle').value.trim();
  const description = document.getElementById('taskDesc').value.trim();
  const priority = parseInt(document.getElementById('taskPriority').value) || 3;
  const deadline = document.getElementById('taskDeadline').value || null;

  if (!title) {
    alert('Введіть назву завдання');
    return;
  }

  const payload = {
    title,
    description,
    priority,
    deadline
  };

  const res = await fetch(`${API_URL}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.status !== 201) {
    alert('Помилка при створенні задачі');
    return;
  }

  document.getElementById('addForm').reset();
  loadTasks();
}

async function deleteTask(id) {
  const ok = confirm('Видалити цю задачу?');
  if (!ok) return;
  const res = await fetch(`${API_URL}/tasks/${id}`, { method: 'DELETE' });
  if (res.status !== 204) {
    alert('Помилка при видаленні');
    return;
  }
  loadTasks();
}


function renderTasks(tasks) {
  const ul = document.getElementById('taskList');
  ul.innerHTML = '';

  if (!tasks.length) {
    ul.innerHTML = '<li>No tasaks</li>';
    return;
  }

  for (const t of tasks) {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${t.title}</strong> — ${t.description || ''} 
      [${t.done ? 'done' : 'pending'}]
      <br>Priority: ${t.priority}, Deadline: ${t.deadline || '-'}
      <button onclick="deleteTask(${t.id})">DELETE</button>
    `;
    ul.appendChild(li);
  }
}


window.addEventListener('load', loadTasks);
