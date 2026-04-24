from dataclasses import dataclass, field
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


@dataclass
class Consumption:
    total_m3: float = 0.0
    delta_l: float = 0.0

    def __post_init__(self):
        self.total_m3 = max(Decimal("0.0"), to_decimal(self.total_m3))
        self.delta_l = max(Decimal("0.0"), to_decimal(self.delta_l))

    def to_dict(self):
        return {
            "total_m3": float(round_decimal(self.total_m3, 2)),
            "delta_l": float(round_decimal(self.delta_l, 2)),
        }


@dataclass
class Device:
    STATES = ["ok", "error", "warning"]

    meter_id: str = "WTR-000000"
    timestamp: datetime = None
    consumption: Consumption = None
    status: str = "error"
    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        self.meter_id = self.norm_id(self.meter_id)
        self.timestamp = self.norm_time(self.timestamp)
        self.consumption = self.norm_consumption(self.consumption)
        self.status = self.norm_status(self.status)
        self.errors = self.norm_errors(self.errors)
        self.validate()

    def norm_id(self, v):
        return str(v).strip().upper()

    def norm_time(self, v):
        if v is None:
            return None
        if isinstance(v, str):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        if isinstance(v, datetime):
            if v.tzinfo is not None:
                return v.astimezone(timezone.utc).replace(tzinfo=None)
            return v
        return None

    def norm_status(self, v):
        v = str(v).lower().strip()
        return v if v in self.STATES else "error"

    def norm_errors(self, v):
        return v if v else []

    def norm_consumption(self, v):
        if v is None:
            return None
        if isinstance(v, dict):
            return Consumption(
                total_m3=v.get("total_m3", 0.0),
                delta_l=v.get("delta_l", 0.0),
            )
        return v

    def validate(self):
        if self.consumption is None and self.status != "error":
            self.status = "warning"

        if self.status == "ok":
            self.errors = []
        elif self.status != "ok" and not self.errors:
            self.errors = ["Unexpected error"]

    def format_time(self):
        if self.timestamp is None:
            return None
        return self.timestamp.replace(tzinfo=None).isoformat(timespec="seconds")

    def to_dict(self):
        return {
            "meter_id": self.meter_id,
            "timestamp": self.format_time(),
            "consumption": self.consumption.to_dict() if self.consumption else None,
            "status": self.status,
            "errors": self.errors,
        }


@dataclass
class Devices:
    data_list: list[dict]
    devices: list[Device] = field(init=False)

    def __post_init__(self):
        self.devices = [Device(**item) for item in self.data_list]

    def to_dictlist(self):
        return [dev.to_dict() for dev in self.devices]



if __name__ == "__main__":
    data = {
        'meter_id': 'WTR-100023',
        'timestamp': '2026-04-10T12:39:53.411498Z',
        'consumption': {'total_m3': 6309.57, 'delta_l': 46},
        'status': "error",
        'errors': []
    }

    device = Device(**data)
    print(device.to_dict())

    devices = Devices([data, data, data])
    print(devices.to_dictlist())