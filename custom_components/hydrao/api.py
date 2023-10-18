import logging
import aiohttp
from aiohttp.client import ClientTimeout, ClientError
from datetime import datetime, timedelta
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_API_KEY
from .const import AUTH_URL, DATA_URL, ME_URL, CLIENT_TIMEOUT,ERROR_MESSAGE_429, STAT_URL


_LOGGER = logging.getLogger(__name__)


class HydraoAPI:
    """Api to get Hydrao data"""

    def __init__(
        self, config, session: aiohttp.ClientSession = None, timeout=CLIENT_TIMEOUT
    ) -> None:
        self._timeout = timeout
        if session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()
        self._config = config
        self._token = None
        self._data = None
        self._headers={}
        # self._expiry = None

    async def async_get_token(self):
        """Get user token to allow request"""
        self._headers={
                    "x-api-key": self._config[CONF_API_KEY],
                    "Content-type" : "application/json"
                }
        request = await self._session.post(
            AUTH_URL,
            headers = self._headers,
            json={
                "email": self._config[CONF_EMAIL],
                "password": self._config[CONF_PASSWORD],
            },
        )
        if request.status == 200:
            resp = await request.json()
            self._token = resp["access_token"]
            # self._expiry = datetime.now()+timedelta(seconds=int(resp["expires_in"]))
            _LOGGER.debug("Got response %s ", resp)
            # _LOGGER.debug("Token will expire at  %s ", self._expiry)
        elif request.status ==429: #Too many request
            _LOGGER.error(
                ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
               'Failed to get token with status %s', request.status
            )
            raise ValueError

    async def async_get_devices(self):
        if not self._token:
            await self.async_get_token()
        self._headers["Authorization"]=f"Bearer {self._token}"
        request = await self._session.get(
            DATA_URL,
            headers = self._headers,
        )
        if request.status == 200:
            resp = await request.json()
            _LOGGER.debug("got response %s ", resp)
            return resp
        elif request.status ==429: #Too many request
            _LOGGER.error(
              ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
                "Failed to get devices list info, with status %s ", request.status
            )
            raise ValueError

    async def get_device_details(self, uuid):
        if not self._token:
            await self.async_get_token()
        self._headers["Authorization"]=f"Bearer {self._token}"
        request = await self._session.get(
            f"{DATA_URL}/{uuid}",
            headers = self._headers,
        )
        if request.status == 200:
            resp = await request.json()
            _LOGGER.debug("got response %s ", resp)
            return resp
        elif request.status == 429: #Too many request
            _LOGGER.error(
               ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
                "Failed to get device info, with status %s ", request.status
            )
            raise ValueError

    async def async_get_device_stat(self, uuid):
        """Get device stat"""
        if not self._token :
            _LOGGER.debug('## No token or token expired, need to get a new one')
            await self.async_get_token()
        self._headers["Authorization"]=f"Bearer {self._token}"
        request = await self._session.get(
            f"{DATA_URL}/{uuid}/stats",
            headers = self._headers,
        )
        if request.status == 200:
            resp = await request.json()
            _LOGGER.debug("got response %s ", resp)
            self._data= resp
            return resp
        elif request.status == 429: #Too many request
            _LOGGER.error(
               ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
                "Failed to get devices info, with status %s ", request.status
            )
            raise ValueError

    async def async_get_user_data(self):
        """Get user data"""
        if not self._token or datetime.now()> self._expiry:
            _LOGGER.debug('## No token or token expired, need to get a new one')
            await self.async_get_token()

        request = await self._session.get(
            ME_URL,
            headers = self._headers,
        )
        if request.status == 200:
            resp = await request.json()
            _LOGGER.debug("got response %s ", resp)
            self._data= resp
            return resp
        elif request.status == 429: #Too many request
            _LOGGER.error(
               ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
                "Failed to get devices info, with status %s ", request.status
            )
            raise ValueError
    async def async_get_stat(self):
        """Get stat"""
        if not self._token or datetime.now()> self._expiry:
            _LOGGER.debug('## No token or token expired, need to get a new one')
            await self.async_get_token()

        request = await self._session.get(
            STAT_URL,
            headers = self._headers,
        )
        if request.status == 200:
            resp = await request.json()
            _LOGGER.debug("got response %s ", resp)
            self._data= resp
            return resp
        elif request.status == 429: #Too many request
            _LOGGER.error(
               ERROR_MESSAGE_429
            )
            raise ValueError
        else:
            _LOGGER.error(
                "Failed to get devices info, with status %s ", request.status
            )
            raise ValueError

    def get_key(self, key):
        """Get value for the given key in JSON Data"""
        if self._data is not None:
            return self._data.get(key)
        else:
            return ""