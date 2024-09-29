import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt import (
    async_subscribe,
)

from .constants import DOMAIN
from .coordinator import OpenWRTMqttCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug(entry.data)

    # Create the Data Coordinator
    coordinator = OpenWRTMqttCoordinator(hass, entry)

    # First data update
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register the new sensors platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle unloading of a config entry."""
    # Unsubscribe all the entities registered under the platform
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, ["sensor", "light"])
    
    # If everything was ok
    if unload_ok:
        _LOGGER.debug("Deleting all!")
        # Get the coordinator
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)

        # and if exists unsubscribe from the topic
        if coordinator:
            await coordinator.async_unsubscribe_from_topic()  # Desuscribirse de MQTT (si es necesario)

        # Delete all the data asociated to the configuration entry
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok