from dataclasses import dataclass
from collections.abc import Callable
from homeassistant.const import Platform
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)


DOMAIN="hydrao"
NAME = "Hydrao"
PLATFORMS: list[Platform] = [Platform.SENSOR]
BASE_URL="https://api.hydrao.com/"
AUTH_URL = f"{BASE_URL}sessions"
DATA_URL = f"{BASE_URL}shower-heads"
REFRESH_INTERVALL = 60
CLIENT_TIMEOUT = 10
TITLE= "Hydrao"
ERROR_MESSAGE_429 = "Too Many request response from Hydrao. Can't handle the request. Please try later"
CONF_DEVICES = "devices"

@dataclass
class HydraoRequiredKeysMixin:
    """Mixin for required keys."""
    json_key: str

@dataclass
class HydraoShowerSensorEntityDesc(SensorEntityDescription,HydraoRequiredKeysMixin):
    """Describes Hydrao shower sensor entity."""

SHOWER_SENSOR: tuple[HydraoShowerSensorEntityDesc, ...] =(
    HydraoShowerSensorEntityDesc(
        key="total",
        name="Volume total",
        unit_of_measurement="L",
        icon= "mdi:water",
        json_key="total_volume",

    ),
        HydraoShowerSensorEntityDesc(
        key="average",
        name="Volume moyen",
        unit_of_measurement="L",
        icon= "mdi:water",
        json_key="volume_average"
    ),
    HydraoShowerSensorEntityDesc(
        key="trend",
        name="Tendance",
        json_key="trend",
        unit_of_measurement="%"
        icon="mdi:chart-line-variant"
    ),
    HydraoShowerSensorEntityDesc(
        key="nb",
        name="Nombre",
        json_key="nb_items",
        icon="mdi:pound"
    )
)