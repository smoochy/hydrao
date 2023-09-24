import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
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
#         pass