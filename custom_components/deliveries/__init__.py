"""
Component for handling package Deliveries data.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/deliveries/
"""
from datetime import timedelta
import logging

from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

ATTR_ATTRIBUTION = 'attribution'
ATTR_TRACKING_ID = 'tracking_id'
ATTR_SENDER = 'sender'
ATTR_RECIPIENT = 'recipient'
ATTR_STATUS = 'status'
ATTR_DELIVERY_TIME = 'delivery_time'
ATTR_DELIVERY_WINDOW_MIN = 'delivery_window_min'
ATTR_DELIVERY_WINDOW_MAX = 'delivery_window_max'
ATTR_WEIGHT = 'weight'
ATTR_SIZE = 'size'

DOMAIN = 'deliveries'

ENTITY_ID_FORMAT = DOMAIN + '.{}'

SCAN_INTERVAL = timedelta(seconds=300)

PROP_TO_ATTR = {
    'attribution': ATTR_ATTRIBUTION,
    'tracking_id': ATTR_TRACKING_ID,
    'sender': ATTR_SENDER,
    'recipient': ATTR_RECIPIENT,
    'status': ATTR_STATUS,
    'delivery_time': ATTR_DELIVERY_TIME,
    'delivery_window_min': ATTR_DELIVERY_WINDOW_MIN,
    'delivery_window_max': ATTR_DELIVERY_WINDOW_MAX,
    'weight': ATTR_WEIGHT,
    'size': ATTR_SIZE,
}


async def async_setup(hass, config):
    """Set up the deliveries component."""
    component = hass.data[DOMAIN] = EntityComponent(
        _LOGGER, DOMAIN, hass, SCAN_INTERVAL)
    await component.async_setup(config)
    return True


async def async_setup_entry(hass, entry):
    """Set up a config entry."""
    return await hass.data[DOMAIN].async_setup_entry(entry)


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.data[DOMAIN].async_unload_entry(entry)


class DeliveriesEntity(Entity):
    """ABC for deliveries data."""

    @property
    def tracking_id(self):
        """Return the tracking id code."""
        return None

    @property
    def sender(self):
        """Return the sender's details."""
        return None

    @property
    def recipient(self):
        """Return the recipient's details."""
        return None

    @property
    def status(self):
        """Return the status of the package."""
        return None

    @property
    def delivery_time(self):
        """Return the date and time when the package was delivered."""
        return None

    @property
    def delivery_window_min(self):
        """Return the low end of the delivery window."""
        return None

    @property
    def delivery_window_max(self):
        """Return the high end of the delivery window."""
        return None

    @property
    def attribution(self):
        """Return the attribution."""
        return None

    @property
    def weight(self):
        """Return the weight of the package."""
        return None

    @property
    def size(self):
        """Return the size of the package."""
        return None

    @property
    def state_attributes(self):
        """Return the state attributes."""
        data = {}

        for prop, attr in PROP_TO_ATTR.items():
            value = getattr(self, prop)
            if value is not None:
                data[attr] = value

        return data

    @property
    def state(self):
        """Return the current state."""
        return self.tracking_id
