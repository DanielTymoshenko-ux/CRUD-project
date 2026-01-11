const express = require("express");
const db = require("./db");
const path = require("path");
const app = express();
const PORT = 5000;

app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

function validateTask(body) {
    if (!body.title || typeof body.title !== "string") {
        return "Title is required and must be a string";
    }
    if (body.priority && (body.priority < 1 || body.priority > 5)) {
        return "Priority must be between 1 and 5";
    }
    return null;
}


app.get("/api/tasks", (req, res) => {
    const tasks = db.prepare("SELECT * FROM tasks ORDER BY id DESC").all();
    res.json(tasks);
});

// GET ONE
app.get("/api/tasks/:id", (req, res) => {
    const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
    if (!task) return res.status(404).json({ error: "Not found" });
    res.json(task);
});


app.post("/api/tasks", (req, res) => {
    const error = validateTask(req.body);
    if (error) return res.status(400).json({ error });

    const stmt = db.prepare(`
        INSERT INTO tasks (title, description, priority, deadline, done, created_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
    `);

    const result = stmt.run(
        req.body.title,
        req.body.description || "",
        req.body.priority || 3,
        req.body.deadline || null,
        req.body.done ? 1 : 0
    );

    const newTask = db.prepare("SELECT * FROM tasks WHERE id = ?").get(result.lastInsertRowid);
    res.status(201).json(newTask);
});


app.put("/api/tasks/:id", (req, res) => {
    const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
    if (!task) return res.status(404).json({ error: "Not found" });

    const stmt = db.prepare(`
        UPDATE tasks
        SET title = ?, description = ?, priority = ?, deadline = ?, done = ?
        WHERE id = ?
    `);

    stmt.run(
        req.body.title || task.title,
        req.body.description || task.description,
        req.body.priority || task.priority,
        req.body.deadline || task.deadline,
        req.body.done ? 1 : 0,
        req.params.id
    );

    const updated = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
    res.json(updated);
});


app.delete("/api/tasks/:id", (req, res) => {
    db.prepare("DELETE FROM tasks WHERE id = ?").run(req.params.id);
    res.status(204).send();
});

app.listen(PORT, () => console.log(`Server running on http://127.0.0.1:${PORT}`));
