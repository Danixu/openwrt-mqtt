import logging
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .coordinator import MqttSensorCoordinator

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    _LOGGER.setLevel(logging.DEBUG)
    return True

async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["devices"] = {}
    device_id = entry.data.get("id")

    # Crear un coordinador para el dispositivo
    coordinator = MqttSensorCoordinator(hass, entry)
    hass.data[DOMAIN]["devices"][device_id] = coordinator

    return True
