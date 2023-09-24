""" Implements the sensors component """
import logging
from typing import Any, Coroutine
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from .api import (HydraoAPI)
from .__init__ import (HydraoApiCoordinator)
from .const import (
    DOMAIN,
    SHOWER_SENSOR,
    TITLE,
    CONF_DEVICES,
    HydraoShowerSensorEntityDesc,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Configuration"""
    config = hass.data[DOMAIN][entry.entry_id]
    api = config["hydraoapi"]
    entities=[]
    for shower_uuid in entry.options.get(CONF_DEVICES):
        shower_info = await api.get_device_details(shower_uuid)
        entities.extend(
            HydraoShower(hass, config, sensor_description,api,
                         coordinator=config[shower_uuid],
                         shower_info=shower_info)
            for sensor_description in SHOWER_SENSOR
        )
    async_add_entities(entities, True)

class HydraoShower(SensorEntity, CoordinatorEntity):

    def __init__(
        self,
        hass: HomeAssistant,
        entry_infos,
        description: HydraoShowerSensorEntityDesc,
        api: HydraoAPI,
        coordinator : HydraoApiCoordinator,
        shower_info #details on the device
        ) -> None:
        super().__init__(coordinator)
        self._hass = hass
        self.entity_description = description
        self._attr_name = f"{shower_info['label']}-{description.name}"
        self._attr_unique_id = f"{shower_info['mac_address']}-{description.name}"
        self._uuid = f"{shower_info['device_uuid']}"
        self._coordinator = coordinator
        self._attr_device_class = description.device_class
        self._attr_unit_of_measurement = description.unit_of_measurement
        self._attr_extra_state_attributes = {
            "Dernière de mise à jour":shower_info['last_sync_date'],
        }

        self._attr_device_info = DeviceInfo(
            name=f"{shower_info['label']}",
            identifiers={
                (DOMAIN, f"{shower_info['device_uuid']}-{shower_info['label']}")
            },
            manufacturer="Hydrao",
            model=f"{shower_info['type']}",
            hw_version=f"{shower_info['hw_version']}",
            sw_version=f"{shower_info['fw_version']}"

        )
        self._api= api
        _LOGGER.debug("Creating an Hydrao sensor, named %s", self.name)



    @property
    def native_value(self):
        value = self._api.get_key(self.entity_description.json_key)
        return value
