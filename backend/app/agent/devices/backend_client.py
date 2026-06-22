import requests

BACKEND_URL = "https://wa16zqfai5.execute-api.us-east-1.amazonaws.com/prod"

_DEFAULT_POWER: dict[str, float] = {
    "Heat pump": 2.1,
    "EV charger": 7.2,
    "Kitchen": 0.8,
    "HVAC": 1.4,
    "Water heater": 3.0,
    "Solar inverter": 0.2,
    "Dishwasher": 1.5,
    "Fan": 0.3,
}


def get_devices():
    response = requests.get(
        f"{BACKEND_URL}/api/v1/devices",
        timeout=10
    )
    response.raise_for_status()
    devices = response.json()

    print("GET_DEVICES RESPONSE:")
    print(devices)

    return devices


def update_device(device_id: int, status: str):
    response = requests.patch(
        f"{BACKEND_URL}/api/v1/devices/{device_id}",
        json={"status": status},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()

    print("UPDATE_DEVICE RESPONSE:")
    print(result)

    return result

def get_default_power():
    """Get the default power mapping"""
    return _DEFAULT_POWER