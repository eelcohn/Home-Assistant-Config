"""
Demo platform that offers fake packet delivery data.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""

from homeassistant.components.deliveries import DeliveriesEntity


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Deliveries."""
    add_entities([
        DemoDelivery('1Z0715X10190647079', 'Sender name & such, 5007 South Park Drive, Durham NC 27713', 'Recipient name & such, 123 Bishop Road, Honolulu HI 96819', now(), now(), now(), 3000, '20x30x40'),
        DemoDelivery('3SABCD100001234', 'Verzender, Kerkstraat 10, 1234 AA Kerkhuizen', 'Ontvanger, Hoofdweg 230a, 9999 XX Geenplaatsen', now(), now(), now(), 800, '15x20x10'),
    ])


class DemoDelivery(DeliveriesEntity):
    """Representation of Delivery data."""

    def __init__(self, name, tracking_id, sender, recipient, status, delivery_time, delivery_window_min, delivery_window_max, weight, size):
        """Initialize the Demo Delivery."""
        self._name = name
        self._tracking_id = tracking_id
        self._sender = sender
        self._recipient = recipient
        self._status = status
        self._delivery_time = delivery_time
        self._delivery_window_min = delivery_window_min
        self._delivery_window_max = delivery_window_max
        self._weight
        self._size

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format('Demo package delivery courier', self._name)

    @property
    def should_poll(self):
        """No polling needed for Demo platform."""
        return False

    @property
    def tracking_id(self):
        """Return the tracking id code."""
        return self._tracking_id

    @property
    def sender(self):
        """Return the sender's details."""
        return self._sender

    @property
    def recipient(self):
        """Return the recipient's details."""
        return self._recipient

    @property
    def status(self):
        """Return the status of the package."""
        return self._status

    @property
    def delivery_time(self):
        """Return the date and time when the package was delivered."""
        return self._delivery_time

    @property
    def delivery_window_min(self):
        """Return the low end of the delivery window."""
        return self._delivery_window_min

    @property
    def delivery_window_max(self):
        """Return the high end of the delivery window."""
        return self._delivery_window_max

    @property
    def weight(self):
        """Return the weight of the package."""
        return self._weight

    @property
    def size(self):
        """Return the size of the package."""
        return self._size

    @property
    def attribution(self):
        """Return the attribution."""
        return 'Powered by Home Assistant'

