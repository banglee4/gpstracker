from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

# Serve frontend (index.html di /static)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

class GPSData(BaseModel):
    device_id: str
    lat: float
    lon: float
    timestamp: datetime = datetime.now()

@app.post("/api/gps")
def receive_gps(data: GPSData):
    conn = sqlite3.connect("gps.db")
    c = conn.cursor()
    c.execute("INSERT INTO gps (device_id, lat, lon, timestamp) VALUES (?, ?, ?, ?)",
              (data.device_id, data.lat, data.lon, data.timestamp))
    conn.commit()
    conn.close()
    return {"status": "ok"}

@app.get("/api/latest")
def latest_positions():
    conn = sqlite3.connect("gps.db")
    c = conn.cursor()
    c.execute("SELECT device_id, lat, lon, timestamp FROM gps ORDER BY timestamp DESC LIMIT 10")
    rows = c.fetchall()
    conn.close()
    return {"data": rows}
