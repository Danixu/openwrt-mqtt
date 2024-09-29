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

    # Crear el coordinador de datos
    coordinator = OpenWRTMqttCoordinator(hass, entry)

    # Primera actualización de datos
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register the new sensors platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle unloading of a config entry."""
    # Desuscribir todas las entidades registradas bajo la plataforma
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, ["sensor", "light"])
    
    # Si se descargaron las plataformas correctamente
    if unload_ok:
        _LOGGER.debug("Deleting all!")
        # Obtener el coordinador desde los datos de Home Assistant
        coordinator = hass.data[DOMAIN].get(config_entry.entry_id)

        # Si existe el coordinador, desuscribirse y cancelar sus tareas
        if coordinator:
            await coordinator.async_unsubscribe_from_topic()  # Desuscribirse de MQTT (si es necesario)
            coordinator.async_cancel()  # Cancelar actualizaciones periódicas o tareas asíncronas

        # Eliminar los datos asociados a la entrada de configuración
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok