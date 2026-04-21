import json
import time
import random
from datetime import datetime

ERROR_CODES = [
    "sensor_fault", "low_battery", "tamper_detected",
    "comm_timeout", "valve_stuck", "over_pressure"
]

def mock_reader():
    while True:
        try:
            with open("data.json", encoding="UTF-8") as f:
                data = json.load(f)
            data["timestamp"] = datetime.now().isoformat()
            data["consumption"]["total_m3"] = round(random.uniform(5.0, 8500.0), 2)
            data["consumption"]["delta_l"] = random.randint(0, 500)
            data["status"] = random.choice(["ok", "error"])
            if data["status"] != 'ok':
                data["errors"] = random.sample(ERROR_CODES, k=random.randint(1, 2))

            yield data

        except Exception as e:
            print(e)

        time.sleep(3)