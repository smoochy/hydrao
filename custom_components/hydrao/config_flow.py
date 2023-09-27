import logging
import voluptuous as vol
from typing import Any, Dict, Optional
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_registry import (
    async_entries_for_config_entry,
    async_get,

)
from homeassistant import config_entries
from homeassistant.core import  callback
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_API_KEY,CONF_DEVICES
from .const import DOMAIN, TITLE
from .api import HydraoAPI

_LOGGER = logging.getLogger(__name__)


AUTHENT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL, default=""): cv.string,
        vol.Required(CONF_PASSWORD, default=""): cv.string,
        vol.Required(CONF_API_KEY, default="") : cv.string
    }
)
async def validate_credentials(client: any, data: dict) -> None:
    """Validate user credential to access API"""
    try:
        await client.async_get_token()
    except ValueError as exc:
        raise exc

async def get_devices(client: any, data: dict) -> None:
    """Return the devices associated to the account"""
    try:
       return await client.async_get_devices()
    except ValueError as exc:
        raise exc


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hydrao component"""
    def __init__(self):
        """Initialize"""
        self.data = None


    @callback
    def _show_setup_form(self, step_id=None, user_input=None, schema=None, errors=None):
        """Show the form to the user."""
        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id=step_id,
            data_schema=schema,
            errors=errors or {},
        )
    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        _LOGGER.debug("In async_step_user !!")

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_EMAIL].lower())
            self._abort_if_unique_id_configured()
            session = async_get_clientsession(self.hass)
            self._client= HydraoAPI(config=user_input,session=session)
            try:
                await validate_credentials(self._client, user_input)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                self.data = user_input
                return await self.async_step_devices()
        return self._show_setup_form("user", user_input, AUTHENT_SCHEMA, errors)

    async def async_step_devices(self, user_input=None):
        errors = {}
        _LOGGER.debug("In async_step_devices !!")
        if user_input is None:
            try:
                devices = await get_devices(self._client, user_input)
                device_list={}
                device_list= { device['device_uuid']: device['label'] for device in devices}
            except ValueError:
                errors["base"] = "devices"
            if not errors:
                # self.data = user_input
                data_schema= vol.Schema(
                    {vol.Required(CONF_DEVICES):cv.multi_select(device_list)}
                )
                return self._show_setup_form("devices", user_input, data_schema, errors)

        self.data[CONF_DEVICES]=user_input[CONF_DEVICES]
        return self.async_create_entry(title=TITLE,
                                       data=self.data,
                                       options={CONF_DEVICES: user_input[CONF_DEVICES]})
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return HydraoOptionsFlowHandler(config_entry)

class HydraoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
            self, user_input: Dict[str, Any] = None
        ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}
        entity_registry = await async_get_registry(self.hass)
        entries = async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id
        )
        all_devices = {e.entity_id: e.original_name for e in entries}
        device_map = {e.entity_id: e for e in entries}
        if user_input is not None:
            updated_devices = deepcopy(self.config_entry.data[CONF_DEVICES])

            # Remove any unchecked repos.
            removed_entities = [
                entity_id
                for entity_id in device_map.keys()
                if entity_id not in user_input["devices"]
            ]
            for entity_id in removed_entities:
                entity_registry.async_remove(entity_id)
                # Remove from our configured repos.
                entry = device_map[entity_id]
                entry_path = entry.unique_id
                updated_device = [e for e in updated_device if e["devices"] != entry_path]
            if not errors :
                return self.async_create_entry(
                    title="",
                    data={CONF_DEVICES: updated_devices},
                )
        try:
            devices = await get_devices(self._client, user_input) # get device list
            device_list={}
            device_list= { device['device_uuid']: device['label'] for device in devices}
        except ValueError:
            errors["base"] = "devices"
        #TODO compare device list from api & from entity registry to fill all_device and check the one already existing in HA
        options_schema = vol.Schema(
            {
                vol.Optional("devices", default=list(all_devices.keys())): cv.multi_select(
                    all_devices
                ),
            }
        )
        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )