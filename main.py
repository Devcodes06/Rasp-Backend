from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import threading
import os

from sensors.all_sensors import sensor_loop, latest_sensor_data

app = FastAPI()

# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== START SENSOR THREAD =====================
@app.on_event("startup")
def startup():
    thread = threading.Thread(target=sensor_loop, daemon=True)
    thread.start()
    print("Sensor background thread started")

# ===================== API =====================
@app.get("/api/sensor-data")
def sensor_data():
    if latest_sensor_data["timestamp"] is None:
        return {
            "status": "warming_up",
            "message": "Sensor data not ready yet"
        }
    return latest_sensor_data

