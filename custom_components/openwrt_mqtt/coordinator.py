import json
import logging
from .sensor import TemperatureSensor, HumiditySensor
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.components import mqtt
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

class MqttSensorCoordinator(DataUpdateCoordinator):
    """Coordinador para manejar la actualización de sensores MQTT."""

    def __init__(self, hass, entry):
        """Inicializar el coordinador."""
        self.hass = hass
        self.device_id = entry.data.get("id")
        self.topic = entry.data.get("mqtt_topic")
        self.hass = hass
        self.sensors = {}

        _LOGGER.setLevel(logging.DEBUG)
        # Suscribirse al topic
        hass.async_create_task(mqtt.async_subscribe(hass, self.topic, self.message_received))

    def get_or_create_sensor(self, sensor_id, sensor_type):
        """Obtener o crear un sensor basado en su tipo."""
        _LOGGER.debug("Get or create the sensor")
        if sensor_id not in self.sensors:
            _LOGGER.debug("The sensor is new, so will be created.")
            if sensor_type == "temperature":
                _LOGGER.debug("The sensor is a temperature sensor.")
                sensor = TemperatureSensor(self.device_id, sensor_id)
            elif sensor_type == "humidity":
                _LOGGER.debug("The sensor is a humidity sensor.")
                sensor = HumiditySensor(self.device_id, sensor_id)
            else:
                _LOGGER.warning(f"Unknown sensor type: {sensor_type}")
                return None
            
            _LOGGER.debug("Returning the new created sensor.")
            self.sensors[sensor_id] = sensor
            return sensor
        
        _LOGGER.debug("The sensor already exists. Returning the sensor.")
        return self.sensors[sensor_id]

    @callback
    async def message_received(self, msg):
        """Manejar nuevos mensajes MQTT."""
        _LOGGER.debug(f"Received message in topic {msg.topic} with data {msg.payload}")
        payload = json.loads(msg.payload)
        sensor_id = payload.get("id")
        entity_id = payload.get("ent")
        sensor_type = payload.get("type")

        if sensor_id and entity_id and sensor_type:
            _LOGGER.debug("We have the required data. Creating the sensor.")
            # Obtener o crear el sensor adecuado basado en el tipo
            sensor = self.get_or_create_sensor(sensor_id, sensor_type)

            # Verificar el registro de entidades
            _LOGGER.debug("Verifying the entities registry")
            entity_registry = er.async_get(self.hass)
            existing_entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, entity_id)

            _LOGGER.debug(f"The entity return is: {existing_entity_id}")
            if existing_entity_id is None:
                _LOGGER.debug("The entity doesn't exists so will be created.")
                # Crear la entidad si no existe
                entity_registry.async_get_or_create(
                    domain="sensor",
                    platform=DOMAIN,
                    unique_id=entity_id,
                    suggested_object_id=sensor.name
                )

                # Añadir la entidad a Home Assistant de forma asincrónica
                _LOGGER.debug("Add the entity to HA")
                sensor.register_sensor()

            _LOGGER.debug("The entity was added correctly. Updating data...")
            await sensor.async_write_ha_state()
            sensor.async_update(payload.get("state"), {k: v for k, v in payload.items() if k not in ["id", "ent", "state", "type"]})