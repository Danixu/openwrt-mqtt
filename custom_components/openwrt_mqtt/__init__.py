# __init__.py
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .coordinator import OpenWRTMqttCoordinator

from .constants import DOMAIN, TOPICS_DATA

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Configuración inicial de la integración usando config entry."""
    data = config_entry.as_dict()['data']

    _LOGGER.info(f"Data: {data}")

    # Crear el coordinador de datos para los temas MQTT
    coordinator = OpenWRTMqttCoordinator(hass, data)

    # Almacenar el coordinador en hass.data para que las entidades puedan acceder a él
    hass.data[DOMAIN] = {"coordinator": coordinator}

    # Iniciar el coordinador para suscribirse a los temas MQTT
    await coordinator.async_setup()

    # Cargar plataformas (sensor, etc.)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Desinstalar la integración."""
    # Elimina las entidades relacionadas con la entrada de configuración
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")

    # Eliminar el coordinador de hass.data
    hass.data.pop(DOMAIN)

    return True


"""
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers import service
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.mqtt import (
    async_subscribe,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .constants import DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = entry.as_dict()['data']

    #device = new_coordinator(hass, data, hass.data[DOMAIN]['devices'])

    #await device.coordinator.async_config_entry_first_refresh()
    #hass.data[DOMAIN]['devices'][entry.entry_id] = device
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN]['devices'].pop(entry.entry_id)
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    # Verificar si MQTT está configurado
    if "mqtt" not in hass.config.components:
        _LOGGER.error("MQTT no está configurado. Revisa tu configuración de Home Assistant.")
        return False
    
    hass.data[DOMAIN] = dict(devices={})

    # Acceder a la configuración de MQTT si es necesario
    mqtt_config = hass.data.get("mqtt", {})
    _LOGGER.info(f"Configuración de MQTT: {mqtt_config}")

    # Ejemplo: Suscribirse a un tema específico
    async def mensaje_recibido(topic):
        _LOGGER.info(f"Mensaje recibido en {topic}")

    # Suscribirse a un tema de ejemplo
    #await async_subscribe(hass, "openwrt/#", mensaje_recibido)

    async def async_init(call):
        parts = call.data["name"].split(" ")
        for entry_id in await service.async_extract_config_entry_ids(hass, call):
            device = hass.data[DOMAIN]["devices"][entry_id]


    hass.services.async_register(DOMAIN, "init", async_init)

    _LOGGER.info("Integración MQTT personalizada configurada correctamente.")
    return True

class OpenWrtEntity(CoordinatorEntity):
    def __init__(self, device, device_id: str):
        super().__init__(device.coordinator)
        self._device_id = device_id
        self._device = device

    @property
    def device_info(self):
        return {
            "identifiers": {
                ("id", self._device_id)
            },
            "name": f"OpenWrt [{self._device_id}]",
            "model": self.data["info"]["model"],
            "manufacturer": self.data["info"]["manufacturer"],
            "sw_version": self.data["info"]["sw_version"],
        }

    @property
    def name(self):
        return "OpenWrt [%s]" % (self._device_id)

    @property
    def unique_id(self):
        return "sensor.openwrt.%s" % (self._device_id)

    @property
    def data(self) -> dict:
        return self.coordinator.data

"""