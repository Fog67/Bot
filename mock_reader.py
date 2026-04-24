import json
import time
import random
from datetime import datetime

err_codes = [
    "sensor_fault", "low_battery", "tamper_detected",
    "comm_timeout", "valve_stuck", "over_pressure"
]

id_s = [f"WTR-{random.randint(100000,999999)}" for _ in range(10)]

def mock_reader():
    while True:
        try:
            reqs = []
            for meter_id in random.sample(id_s, k=10):
                data = {
                    "meter_id": meter_id,
                    "timestamp": datetime.now().isoformat(),
                    "consumption": {
                        "total_m3": round(random.uniform(5.0, 8500.0), 2),
                        "delta_l": random.randint(0, 500)
                    },
                    "status": random.choice(["ok", "error"]),
                    "errors": []
                }

                if random.random() < 0.2:
                    data.pop("timestamp", None)
                if random.random() < 0.2:
                    data.pop("consumption", None)
                if random.random() < 0.1:
                    data.pop("status", None)

                if data.get("status") == "error":
                    data["errors"] = random.sample(err_codes, k=random.randint(1, 2))
                reqs.append(data)
            yield reqs

        except Exception as e:
            print(e)

        time.sleep(3)