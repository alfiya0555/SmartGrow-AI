# simulate_sensor.py
import requests
import random
import time

URL = "http://127.0.0.1:5000/sensor"

while True:
    data = {
        "moisture": round(random.uniform(10, 50), 2),
        "temperature": round(random.uniform(20, 35), 2)
    }
    try:
        print("Sending:", data)
        response = requests.post(URL, json=data)
        print("Response:", response.json())
    except Exception as e:
        print("Error sending data:", e)
    time.sleep(5)  # wait 5 seconds before next reading
