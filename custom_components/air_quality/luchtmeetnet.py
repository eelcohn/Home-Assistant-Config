"""
Support for RIVM Luchtmeetnet Air Quality data.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/air_quality/rivm/
"""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.air_quality import (
    PLATFORM_SCHEMA, AirQualityEntity)
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle

_RESOURCE_STATIONDATA = 'https://api.luchtmeetnet.nl/open_api/stations/{}'
_RESOURCE_AIRQUALITYDATA = 'https://api.luchtmeetnet.nl/open_api/stations/{}/measurements?page=&order=&order_direction=&formula='
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Data provided by Rijksinstituut voor Volksgezondheid en Milieu (RIVM)'

DEFAULT_NAME = 'rivm'

CONF_STATION_ID = 'station_id'

SCAN_INTERVAL = timedelta(minutes=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_NAME default=DEFAULT_NAME): cv.string,
})


async def async_setup_platform(
        hass, config, async_add_entities, discovery_info=None):
    """Set up the RIVM air quality platform."""
    from luchtmeetnet_api import Luchtmeetnet

    name = config.get(CONF_NAME)
    station_id = config[CONF_STATION_ID]

    session = async_get_clientsession(hass)
    lmn_api = LuchtmeetnetData(Luchtmeetnet(station_id, hass.loop, session))

    await lmn_api.async_update()

    if 'data' not in lmn_api.api.data:
        _LOGGER.error("Station %s is not available", station_id)
        return

    station_name = lmn_api.api.data['name'] if name is None else name

    async_add_entities([LuchtmeetnetQuality(station_name, lmn_api)], True)


class LuchtmeetnetQuality(AirQualityEntity):
    """Implementation of an Luchtmeetnet air quality entity."""

    def __init__(self, name, luchtmeetnet):
        """Initialize the air quality entity."""
        self._name = name
        self._luchtmeetnet = luchtmeetnet

    @property
    def name(self):
        """Return the name of the air quality entity."""
        return self._name

    @property
    def nitrogen_monoxide(self):
        """Return the particulate matter 10 level."""
        return self._luchtmeetnet.api.no

    @property
    def nitrogen_dioxide(self):
        """Return the particulate matter 10 level."""
        return self._luchtmeetnet.api.no2

    @property
    def particulate_matter_10(self):
        """Return the particulate matter 10 level."""
        return self._luchtmeetnet.api.pm10

    @property
    def particulate_matter_2_5(self):
        """Return the particulate matter 2.5 level."""
        return self._luchtmeetnet.api.pm25

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    async def async_update(self):
        """Get the latest data from the Luchtmeetnet API."""
        await self._luchtmeetnet.async_update()


class RIVMStationData:
    """Get station data from RIVM."""

    def __init__(self, hass, station_id):
        """Initialize the data object."""
        self._hass = hass
        self._station_id = station_id
        self._features = set()
        self.data = None
        self._session = async_get_clientsession(self._hass)

    def request_feature(self, feature):
        """Register feature to be fetched from RIVM API."""
        self._features.add(feature)

    def _build_url(self, baseurl=_RESOURCE_STATIONDATA):
        url = baseurl.format(self._station_id)

        return url

    async def async_update(self):
        """Get the station data from the RIVM API."""
        try:
            with async_timeout.timeout(10, loop=self._hass.loop):
                response = await self._session.get(self._build_url())
            result = await response.json()
            if "error" in result['response']:
                raise ValueError(result['response']["error"]["description"])
            self.data = result

        except ValueError as err:
            _LOGGER.error("Check RIVM API %s", err.args)

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching RIVM station data: %s", repr(err))


class RIVMAirQualityData:
    """Get air quality data from RIVM."""

    def __init__(self, hass, station_id):
        """Initialize the data object."""
        self._hass = hass
        self._station_id = station_id
        self._features = set()
        self.data = None
        self._session = async_get_clientsession(self._hass)

    def request_feature(self, feature):
        """Register feature to be fetched from RIVM API."""
        self._features.add(feature)

    def _build_url(self, baseurl=_RESOURCE_AIRQUALITYDATA):
        url = baseurl.format(self._station_id)

        return url

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        """Get the latest air quality data from the RIVM API."""
        try:
            with async_timeout.timeout(10, loop=self._hass.loop):
                response = await self._session.get(self._build_url())
            result = await response.json()
            if "error" in result['response']:
                raise ValueError(result['response']["error"]["description"])
            self.data = result

        except ValueError as err:
            _LOGGER.error("Check RIVM API %s", err.args)

        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error fetching RIVM air quality data: %s", repr(err))


