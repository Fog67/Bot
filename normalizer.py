from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP


def to_decimal(value, default=Decimal("0.0")):
    try:
        return Decimal(str(value))
    except Exception:
        return default


def round_decimal(value, places=2):
    q = Decimal("1." + "0" * places)
    return value.quantize(q, rounding=ROUND_HALF_UP)


class Consumption:
    def __init__(self, total_m3=0.0, delta_l=0.0):
        self.total_m3 = max(Decimal("0.0"), to_decimal(total_m3))
        self.delta_l = max(Decimal("0.0"), to_decimal(delta_l))

    def to_dict(self):
        return {
            "total_m3": float(round_decimal(self.total_m3, 2)),
            "delta_l": float(round_decimal(self.delta_l, 2)),
        }


class Device:
    norm_statuss = ["ok", "error", "warning"]

    def __init__(self, data: dict):
        self.meter_id = self.norm_id(data.get("meter_id", "WTR-000000"))
        self.timestamp = self.norm_time(data.get("timestamp", datetime.now()))
        self.consumption = self.norm_consumption(data.get("consumption"))
        self.status = self.norm_status(data.get("status", "error"))
        self.errors = self.norm_errors(data.get("errors"))

        self.validate()


    def norm_id(self, v):
        return str(v).strip().upper()

    def norm_time(self, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    def norm_status(self, v):
        v = str(v).lower().strip()
        return v if v in self.norm_statuss else "error"

    def norm_errors(self, v):
        return v if v else []

    def norm_consumption(self, v):
        if v is None:
            return None
        return Consumption(
            total_m3=v.get("total_m3", 0.0),
            delta_l=v.get("delta_l", 0.0),
        )


    def validate(self):
        if self.consumption is None and self.status != "error":
            self.status = "warning"

        if self.status == "ok":
            self.errors = []
        elif self.status != "ok" and not self.errors:
            self.errors = ["Unexpected error"]

    def format_time(self):
        return (
            self.timestamp.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        )

    def to_dict(self):
        return {
            "meter_id": self.meter_id,
            "timestamp": self.format_time(),
            "consumption": self.consumption.to_dict() if self.consumption else None,
            "status": self.status,
            "errors": self.errors,
        }



data = {
    'meter_id': 'WTR-100023',
    'timestamp': '2026-04-10T12:39:53.411498',
    'consumption': {'total_m3': 6309.57, 'delta_l': 46},
    'status': "error",
    'errors': []
}

device = Device(data)
print(device.to_dict())