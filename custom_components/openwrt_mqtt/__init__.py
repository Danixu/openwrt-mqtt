import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt import (
    async_subscribe,
)

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Loading the openwrt mqtt component!: %s", entry.source)
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = {
        "unsubscribe": None,
        "devices": {
            "interface": {},
            "ipstatistics-all": {},
            "load": {},
            "memory": {},
            "processor": {},
            "thermal-cooling": {},
            "thermal-thermal": {},
            "uptime": {},
            "wireless": {}
        }
    }

    # Register the new sensors platform
    _LOGGER.debug("Registering sensors platform.")
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle unloading of a config entry."""
    _LOGGER.debug("Unloading the openwrt mqtt component!. State: %s", config_entry)
    # Unsubscribe all the entities registered under the platform
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, ["sensor"])

    # If everything was ok
    if unload_ok:
        _LOGGER.debug("Unload OK. Removing MQTT subscription if required.")
        # and if exists unsubscribe from the topic
        _unsubscribe = hass.data[DOMAIN].get(config_entry.entry_id)["unsubscribe"]
        if _unsubscribe:
            _LOGGER.debug("The subscription exists, unsubscribing...")
            _unsubscribe()
            hass.data[DOMAIN].get(config_entry.entry_id)["unsubscribe"] = None

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Manejar la eliminación de una config entry."""
    _LOGGER.debug("Removing config entry with id %s", config_entry.entry_id)
    # Verify if the config_entry_id is the same as the integrations id
    if config_entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.debug("Removing integration data for entry %s", config_entry.entry_id)
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    _LOGGER.debug("Cleanup completed for config entry removal.")
