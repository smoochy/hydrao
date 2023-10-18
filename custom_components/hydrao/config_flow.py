""" Config Flow for the component """
import logging
from copy import deepcopy
from typing import Any, Dict
import voluptuous as vol
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import (
    device_registry as dr,
    # entity_registry as er,
    config_validation as cv
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
async def validate_credentials(client: any) -> None:
    """Validate user credential to access API"""
    try:
        await client.async_get_token()
    except ValueError as exc:
        raise exc

async def get_devices(client: any) -> None:
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
                await validate_credentials(self._client)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                self.data = user_input
                return await self.async_step_devices()
        return self._show_setup_form("user", user_input, AUTHENT_SCHEMA, errors)

    async def async_step_devices(self, user_input=None):
        """Select devices to use"""
        errors = {}
        _LOGGER.debug("In async_step_devices !!")
        if user_input is None:
            try:
                devices = await get_devices(self._client)
                device_list={}
                device_list= { device['device_uuid']: device['label'] for device in devices}
            except ValueError:
                errors["base"] = "devices"
            if not errors:
                data_schema= vol.Schema(
                    {vol.Required(CONF_DEVICES):cv.multi_select(device_list)}
                )
                return self._show_setup_form("devices", user_input, data_schema, errors)

        self.data[CONF_DEVICES]=user_input[CONF_DEVICES]
        return self.async_create_entry(title=TITLE,
                                       data=self.data,
                                       options={CONF_DEVICES: user_input[CONF_DEVICES]})
    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     """Get the options flow for this handler."""
    #     return HydraoOptionsFlowHandler(config_entry)

# class HydraoOptionsFlowHandler(config_entries.OptionsFlow):
#     """Handles options flow for the component."""

#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
#         self.config_entry = config_entry

#     async def async_step_init(
#             self, user_input: Dict[str, Any] = None
#         ) -> Dict[str, Any]:
#         """Manage the options for the custom component."""
#         errors: Dict[str, str] = {}
#         # entity_registry = er.async_get(self.hass)
#         # entries = er.async_entries_for_config_entry(
#         #     entity_registry, self.config_entry.entry_id
#         # )
#         device_registry = dr.async_get(self.hass)
#         existing_devices= dr.async_entries_for_config_entry(
#             device_registry,self.config_entry.entry_id)
#         used_devices = {
#             identifier[1]: entry.name
#             for entry in existing_devices
#             for identifier in entry.identifiers
#             if identifier[0] == DOMAIN
#         }
#         # device_map = {: ud for ud in used_devices}
#         if user_input is not None:
#             updated_devices = deepcopy(self.config_entry.data[CONF_DEVICES])
#             # Remove any unchecked devices.
#             removed_entities = [
#                 entry.id
#                 for entry in existing_devices
#                 for identifier in entry.identifiers
#                 if identifier[0] == DOMAIN and identifier[1] not in user_input["devices"]
#             ]
#             for entity_id in removed_entities:
#                 # entity_registry.async_remove(entity_id)
#                 device_registry.async_remove_device(entity_id)
#                 # Remove from our configured repos.
#                 # entry = device_map[entity_id]
#                 # entry_path = entry.unique_id
#                 # updated_device = [e for e in updated_device if e["devices"] != entry_path]
#             if not errors : # ???
#                 return self.async_create_entry(
#                     title=TITLE,
#                     data={CONF_DEVICES: user_input[CONF_DEVICES]}
#                 )
#         try:
#             session = async_get_clientsession(self.hass)
#             self._client= HydraoAPI(config= self.config_entry.data,session=session)
#             await self._client.async_get_token()
#             devices = await get_devices(self._client ) # get device list
#             all_devices={}
#             all_devices= { device['device_uuid']: device['label'] for device in devices}
#             options_schema = vol.Schema(
#                 {
#                     vol.Optional("devices", default=list(used_devices.keys())): cv.multi_select(
#                         all_devices
#                     ),
#                 }
#             )
#             return self.async_show_form(
#                 step_id="init", data_schema=options_schema, errors=errors
#             )
#         except ValueError:
#             errors["base"] = "devices"

