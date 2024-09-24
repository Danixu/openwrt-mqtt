
# sensor.py
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity

from .constants import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Configuración de las entidades del sensor usando el coordinador."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Crear entidades basadas en los temas del coordinador
    sensores = []
    for topic in coordinator.topics:
        sensor = MiSensorMqtt(coordinator, topic)
        sensores.append(sensor)
    
    async_add_entities(sensores)

class MiSensorMqtt(CoordinatorEntity, SensorEntity):
    """Entidad de sensor que utiliza el coordinador de MQTT."""

    def __init__(self, coordinator, topic):
        """Inicializa la entidad del sensor con el coordinador y el tema MQTT."""
        super().__init__(coordinator)
        self._topic = topic
        self._name = f"Sensor basado en {topic}"

    @property
    def name(self):
        """Devuelve el nombre del sensor."""
        return self._name

    @property
    def state(self):
        """Devuelve el estado actual del sensor."""
        # Obtener el último mensaje desde el coordinador
        return self.coordinator.data.get(self._topic)



"""
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory

import logging

from . import OpenWrtEntity
from .constants import DOMAIN

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities
) -> None:
    sensor = MiSensorMqtt("Mi Sensor MQTT")
    async_add_entities([sensor])


class OpenWrtSensor(OpenWrtEntity, SensorEntity):
    def __init__(self, coordinator, device: str):
        super().__init__(coordinator, device)

    @property
    def state_class(self):
        return 'measurement'

class MiSensorMqtt(OpenWrtSensor):
    def __init__(self, device, device_id: str, interface: str):
        super().__init__(device, device_id) 
        self._state = None
        self._name = device_id

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    async def async_update(self):
        # Aquí podrías actualizar el estado con datos de MQTT o de otro recurso
        pass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC
"""