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
    _LOGGER.debug(f"Loading the openwrt mqtt component!: {entry.source}")
    hass.data.setdefault(DOMAIN, {})

    _LOGGER.setLevel(logging.DEBUG)
    _LOGGER.debug(entry.data)

    _LOGGER.debug("Creating the coordinator...")
    # Create the Data Coordinator
    coordinator = OpenWRTMqttCoordinator(hass, entry)

    if not hass.data[DOMAIN].get(entry.entry_id, False):
        _LOGGER.debug("There is no integration data so will be created.")
        hass.data[DOMAIN][entry.entry_id] = {
            "coordinator": coordinator,
            "devices": {},
            "entities": {}
        }
    else:
        _LOGGER.debug("There is integration data. The new coordinator will be created.")
        hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    # First data update
    await coordinator.async_config_entry_first_refresh()

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
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)["coordinator"]

        # and if exists unsubscribe from the topic
        if coordinator:
            _LOGGER.debug("The coordinator exists. Unsuscribing from the MQTT.")
            await coordinator.async_unsubscribe_from_topic()  # Desuscribirse de MQTT (si es necesario)

        # Clear the entities data
        _LOGGER.debug("Clearing the entities entries.")
        hass.data[DOMAIN][config_entry.entry_id]["entities"] = {}

    return unload_ok

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Manejar la eliminación de una config entry."""
    _LOGGER.debug(f"Removing config entry with id {config_entry.entry_id}")

    # Verifica si el config_entry_id es el que corresponde a tu integración
    if config_entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.debug(f"Removing integration data for entry {config_entry.entry_id}")
        hass.data[DOMAIN].pop(config_entry.entry_id, None)

    # Aquí puedes eliminar cualquier otro estado persistente o archivos relacionados.
    _LOGGER.debug("Cleanup completed for config entry removal.")