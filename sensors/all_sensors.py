import time
import threading
import minimalmodbus
import serial

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# ===================== SHARED STATE =====================
latest_sensor_data = {
    "soil": {
        "moisture": None,
        "temperature": None,
        "ec": None,
        "ph": None
    },
    "npk": {
        "nitrogen": None,
        "phosphorus": None,
        "potassium": None
    },
    "water": {
        "raw": None,
        "level_percent": None
    },
    "timestamp": None
}

# ===================== 4-IN-1 SOIL SENSOR =====================
SOIL_PORT = "/dev/ttyUSB0"
SOIL_ID = 1

soil = minimalmodbus.Instrument(SOIL_PORT, SOIL_ID)
soil.serial.baudrate = 9600
soil.serial.bytesize = 8
soil.serial.parity = serial.PARITY_NONE
soil.serial.stopbits = 1
soil.serial.timeout = 1
soil.mode = minimalmodbus.MODE_RTU

# ===================== NPK SENSOR =====================
NPK_PORT = "/dev/ttyUSB1"
NPK_ID = 1

npk = minimalmodbus.Instrument(NPK_PORT, NPK_ID)
npk.serial.baudrate = 4800
npk.serial.bytesize = 8
npk.serial.parity = serial.PARITY_NONE
npk.serial.stopbits = 1
npk.serial.timeout = 1
npk.mode = minimalmodbus.MODE_RTU

# ===================== WATER LEVEL (ADS1115) =====================
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
water_chan = AnalogIn(ads, 1)

DRY_VALUE = 3000
WET_VALUE = 18000

def clamp(val, lo, hi):
    return max(lo, min(val, hi))

# ===================== MAIN SENSOR LOOP =====================
def sensor_loop():
    global latest_sensor_data

    while True:
        try:
            # -------- SOIL SENSOR --------
            latest_sensor_data["soil"]["moisture"] = soil.read_register(0x0000, 0)
            latest_sensor_data["soil"]["temperature"] = soil.read_register(0x0001, 1)
            latest_sensor_data["soil"]["ec"] = soil.read_register(0x0002, 0)
            latest_sensor_data["soil"]["ph"] = soil.read_register(0x0003, 1)

            # -------- NPK SENSOR --------
            latest_sensor_data["npk"]["nitrogen"] = npk.read_register(0, 0)
            latest_sensor_data["npk"]["phosphorus"] = npk.read_register(1, 0)
            latest_sensor_data["npk"]["potassium"] = npk.read_register(2, 0)

            # -------- WATER SENSOR --------
            raw = water_chan.value
            percent = (raw - DRY_VALUE) * 100 / (WET_VALUE - DRY_VALUE)
            percent = clamp(percent, 0, 100)

            latest_sensor_data["water"]["raw"] = raw
            latest_sensor_data["water"]["level_percent"] = round(percent, 1)

            # -------- TIMESTAMP --------
            latest_sensor_data["timestamp"] = time.time()

            print("Sensor snapshot updated")

        except Exception as e:
            print("Sensor read error:", e)

        # ?? FIXED SNAPSHOT INTERVAL
        time.sleep(5)
