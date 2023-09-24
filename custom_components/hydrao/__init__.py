""" Les constantes pour l'intégration Tuto HACS """
import logging
from datetime import timedelta, date
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import  DataUpdateCoordinator
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.components.sensor import (SensorEntity)
from .api import HydraoAPI
from .const import DOMAIN, PLATFORMS,NAME, REFRESH_INTERVALL, CONF_DEVICES

_LOGGER = logging.getLogger(__name__)

PLATFORM: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Initialisation from a config entry."""
    _LOGGER.info(
        "Initializing %s integration with plaforms: %s with config: %s",
        DOMAIN,
        PLATFORMS,
        entry,
    )
    hass.data.setdefault(DOMAIN, {})
    api = HydraoAPI(entry.data)

    devices: list[str] = entry.options[CONF_DEVICES]


    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}
        hass.data[DOMAIN][entry.entry_id]["hydraoapi"]= api
        for device in devices:
            coordinator = HydraoApiCoordinator(hass=hass, config = entry, api=api, uuid=device)
            # await coordinator.async_config_entry_first_refresh() # is it mandatory?
            hass.data[DOMAIN][entry.entry_id][device] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])

    _LOGGER.debug("Setup of %s successful", entry.title)

    return True


class HydraoApiCoordinator(DataUpdateCoordinator):
    """A coordinator to fetch data from the api only once"""

    def __init__(self, hass, config: ConfigType, api, uuid):
        super().__init__(
            hass,
            _LOGGER,
            name=NAME,  # for logging purpose
            update_method=self._update_method,
            update_interval=timedelta(minutes=REFRESH_INTERVALL),
        )
        self.config = config
        self.hass = hass
        self.api = api
        self.uuid = uuid


    async def _update_method(self):
        data = await self.api.async_get_device_stat(self.uuid)
        if data is not None and len(data) > 0:
            return True
        else:
            self.async_set_update_error(
                f'No Data from HYDRAO'
            )
            return False

    async def async_unload_entry(self, hass: HomeAssistant, entry: ConfigEntry) -> bool:
        """This method is called to clean all sensors before re-adding them"""
        _LOGGER.debug("async_unload_entry method called")
        unload_ok = await hass.config_entries.async_unload_platforms(
            entry, [Platform.SENSOR]
        )
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
        return unload_ok
