const Database = require("better-sqlite3");
const db = new Database("todo.db");
db.prepare(`
  CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER,
    deadline TEXT,
    done INTEGER DEFAULT 0,
    created_at TEXT
  );
`).run();

module.exports = db;
