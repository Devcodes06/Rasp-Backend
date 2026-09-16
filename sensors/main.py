from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sensors.all_sensors import start_sensor_threads, latest_sensor_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    start_sensor_threads()

@app.get("/api/sensor-data")
def sensor_data():
    return latest_sensor_data
