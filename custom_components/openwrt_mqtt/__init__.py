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
    _LOGGER.debug("Loading the openwrt mqtt component!")
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug(entry.data)

    _LOGGER.debug("Creating the coordinator...")
    # Create the Data Coordinator
    coordinator = OpenWRTMqttCoordinator(hass, entry)

    # First data update
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # If device data was stored into the DOMAIN then is a reload and must be loaded
    if entry.entry_id in hass.data[DOMAIN].get("devices_data", {}):
        _LOGGER.debug("Devices data found. Will be loaded into the coordinator.")
        coordinator.devices = hass.data[DOMAIN]["devices_data"][entry.entry_id]
        hass.data[DOMAIN]["devices_data"].pop(entry.entry_id)

    # Register the new sensors platform
    _LOGGER.debug("Registering sensors platform.")
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle unloading of a config entry."""
    _LOGGER.debug(f"Unloading the openwrt mqtt component!. State: {config_entry}")
    # Unsubscribe all the entities registered under the platform
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, ["sensor"])
    
    # If everything was ok
    if unload_ok:
        _LOGGER.debug("Getting the coordinator.")
        # Get the coordinator
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)

        # and if exists unsubscribe from the topic
        if coordinator:
            _LOGGER.debug("The coordinator exists. Unsuscribing from the MQTT.")
            await coordinator.async_unsubscribe_from_topic()  # Desuscribirse de MQTT (si es necesario)

        if config_entry.data.get("action") == "reload":
            _LOGGER.debug("Reload action triggered. Storing the data into a temporary variable.")
            # Save the sensors data to restore it later
            if not hass.data[DOMAIN].get("devices_data", False):
                hass.data[DOMAIN]["devices_data"] = {}
            hass.data[DOMAIN]["devices_data"][config_entry.entry_id] = coordinator.devices.copy()
        
        # Delete all the data asociated to the configuration entry
        _LOGGER.debug("Deleting the coordinator data.")
        hass.data[DOMAIN].pop(config_entry.entry_id)

        # Clear the entities data
        _LOGGER.debug("Clearing the entities entries.")
        hass.data[DOMAIN]["entities"] = {}

    return unload_ok