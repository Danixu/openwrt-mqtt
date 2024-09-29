from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .constants import DOMAIN
from .coordinator import MiCoordinadorDeDatos

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})

    # Crear el coordinador de datos
    coordinador = MiCoordinadorDeDatos(hass, entry)

    # Primera actualización de datos
    await coordinador.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinador

    # Registrar la plataforma de sensores
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
