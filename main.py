from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3

# Buat tabel GPS jika belum ada
conn = sqlite3.connect("gps.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS gps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    lat REAL,
    lon REAL,
    timestamp TEXT
)
""")
conn.commit()
conn.close()

app = FastAPI()

# Data model
class GPSData(BaseModel):
    device_id: str
    lat: float
    lon: float
    timestamp: datetime = datetime.now()

# POST endpoint
@app.post("/api/gps")
def receive_gps(data: GPSData):
    conn = sqlite3.connect("gps.db")
    c = conn.cursor()
    c.execute("INSERT INTO gps (device_id, lat, lon, timestamp) VALUES (?, ?, ?, ?)",
              (data.device_id, data.lat, data.lon, data.timestamp))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# GET endpoint
@app.get("/api/latest")
def latest_positions():
    conn = sqlite3.connect("gps.db")
    c = conn.cursor()
    c.execute("SELECT device_id, lat, lon, timestamp FROM gps ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return {"data": rows}

# Mount static files (paling bawah agar tidak override route API)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

DB_PATH = Path("gps.db")
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# Endpoint untuk menampilkan form input
@app.get("/manual", response_class=HTMLResponse)
async def manual_form():
    with open("static/input.html") as f:
        return f.read()

# Endpoint untuk menerima input manual
@app.post("/manual_input")
async def manual_input(device_id: str = Form(...), lat: float = Form(...), lon: float = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gps (device_id, lat, lon) VALUES (?, ?, ?)",
        (device_id, lat, lon)
    )
    conn.commit()
    conn.close()
    return RedirectResponse(url="/manual", status_code=303)
