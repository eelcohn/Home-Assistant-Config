"""
RIVM Luchtmeetnet Air Quality data
Eelco Huininga 2019

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/air_quality/rivm/
"""

VERSION = '1.0.0'

from datetime import datetime, timedelta
from requests import Session

import json
import logging
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.air_quality import PLATFORM_SCHEMA,
    AirQualityEntity
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_NAME, STATE_UNKNOWN)
from homeassistant.util import Throttle

REQUIREMENTS = []

_RESOURCE_STATIONDATA = 'https://api.luchtmeetnet.nl/open_api/stations/{}'
_RESOURCE_AIRQUALITYDATA = 'https://api.luchtmeetnet.nl/open_api/stations/{}/measurements?page=&order=&order_direction=&formula='
_LOGGER = logging.getLogger(__name__)

CONF_PLATE = 'station_id'
CONF_SCAN_INTERVAL = 'scan_interval'
CONF_SENSORS = 'sensors'

DEFAULT_NAME = 'RIVM'
DEFAULT_ATTRIBUTION = 'Data provided by Rijksinstituut voor Volksgezondheid en Milieu (RIVM)'
DEFAULT_SCAN_INTERVAL = timedelta(mninutes=60)

RIVM_DATEFORMAT = '%d/%m/%Y'

SENSOR_TYPES = {
    'nitrogen_monoxide': ['', 'mdi:calendar'],
    'nitrogen_dioxide': ['Nitrogen Dioxide', 'mdi:car'],
    'recall': ['Recall', 'mdi:car'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PLATE): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SENSORS, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
        cv.time_period
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the RIVM Platform."""

    name = config.get(CONF_NAME)
    plate = config.get(CONF_PLATE)
    interval = config.get(CONF_SCAN_INTERVAL)

    data = RIVMSensorData(hass, plate.upper(), interval)

    dev = []
    for sensor_type in config[CONF_SENSORS]:
        dev.append(RIVMSensor(
            hass, data, sensor_type, name,
            plate.upper()))

    add_devices(dev, True)


class RIVMSensor(AirQualityEntity):
    """Representation of a RIVM Sensor."""

    def __init__(self, hass, data, sensor_type, name, plate):
        """Initialize the sensor."""
        self._hass = hass
        self._data = data
        self._sensor_type = sensor_type
        self._name = name
        self._plate = plate
        self._icon = SENSOR_TYPES[sensor_type][1]
        self._state = None
        self._attributes = {ATTR_ATTRIBUTION: DEFAULT_ATTRIBUTION}
        self._unit_of_measurement = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self._name, self._sensor_type)

    @property
    def icon(self):
        """Return the mdi icon of the sensor."""
        return self._icon

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def carbon_dioxide(self):
        """Return the carbon dioxide level."""
        return self._data.co2

    @property
    def carbon_monoxide(self):
        """Return the carbon monoxide level."""
        return self._data.co

    @property
    def nitrogen_oxide(self):
        """Return the nitrogen oxide level."""
        return self._data.n2o

    @property
    def nitrogen_monoxide(self):
        """Return the nitrogen monoxide level."""
        return self._data.no

    @property
    def nitrogen_dioxide(self):
        """Return the nitrogen dioxide level."""
        return self._data.no2

    @property
    def ozone(self):
        """Return the ozone level."""
        return self._data.o3

    @property
    def particulate_matter_0_1(self):
        """Return the particulate matter 0.1 level."""
        return self._data.pm01

    @property
    def particulate_matter_2_5(self):
        """Return the particulate matter 2.5 level."""
        return self._data.pm25

    @property
    def particulate_matter_10(self):
        """Return the particulate matter 10 level."""
        return self._data.pm10

    @property
    def sulphur_dioxide(self):
        """Return the sulphur dioxide level."""
        return self._data.so2

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes    

    def update(self):
        """Fetch new state data for the sensor."""
        self._data.update()

        if self._sensor_type == 'expdate':
            value = self._data.expdate
        elif self._sensor_type == 'insured':
            if self._data.insured == 'Ja':
                value = True
            elif self._data.insured == 'Nee':
                value = False
            else:
                value = None
        elif self._sensor_type == 'recall':
            if self._data.recall == 'Ja':
                value = True
            elif self._data.recall == 'Nee':
                value = False
            else:
                value = None
 
        if value is None:
            value = STATE_UNKNOWN
            self._attributes = {}
        else:
            self._state = value   
            self._attributes = self._data.attrs 

    

class RIVMSensorData(object):
    """
    Get car data from the RIVM API.
    """
    _current_status_code = None
    _interval = DEFAULT_SCAN_INTERVAL

    def __init__(self, hass, plate, interval):
        """
        Initiates the sensor data with default settings if none other are set.
        :param plate: license plate id
        """
        self._hass = hass
        self._plate = plate
        self._interval = interval
        self._session = Session()
        self.no = None
        self.no2 = None
        self.o3 = None
        self.pm01 = None
        self.pm10 = None
        self.pm25 = None
        self.fn = None
        self.c6h6 = None
        self.c7h8 = None
        self.c8h10 = None
        self.co = None
        self.so2 = None
        self.h2s = None
        self.ps = None
        self.nh3 = None

        self.attrs = {}

    def get_data_from_api(self):
        """
        Get data from the RIVM API
        :return: A list containing the RIVM data
        """

        try:
            result = self._session.get(_RESOURCE.format(self._plate), data="json={}")
        except:
            _LOGGER.error("RIVM: Unable to connect to the RIVM API")
            return None

        self._current_status_code = result.status_code

        if self._current_status_code != 200:
            _LOGGER.error("RIVM: Got an invalid HTTP status code %s", self._current_status_code)
            return None

        _LOGGER.debug("RIVM: raw data: %s", result)

        data = result.json()[0]

        return data


    @Throttle(_interval)
    def update(self):
        self.expdate = None
        self.insured = None
        self.recall = None
        self.attrs = {}

        rivm_data = (self.get_data_from_api())

        if rivm_data is not None:
            try:
                self.expdate = datetime.strptime(rivm_data['vervaldatum_apk'], RIVM_DATEFORMAT).date()
            except:
                self.expdate = None
            try:
                self.insured = rivm_data['wam_verzekerd']
            except:
                self.insured = None
            try:
                self.recall = rivm_data['openstaande_terugroepactie_indicator']
            except:
                self.insured = None

