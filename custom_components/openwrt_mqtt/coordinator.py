# coordinator.py
import logging
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .constants import TOPICS_DATA

_LOGGER = logging.getLogger(__name__)

class OpenWRTMqttCoordinator(DataUpdateCoordinator):
    """Coordinador para manejar mensajes MQTT y notificar a las entidades."""

    def __init__(self, hass, hass_data):
        """Inicializa el coordinador con los temas MQTT a suscribirse."""
        super().__init__(
            hass,
            _LOGGER,
            name="OpenWRTMqttCoordinator",
            update_interval=None  # No queremos actualizaciones automáticas por tiempo
        )
        self.hass = hass
        self.topics = TOPICS_DATA
        self.settings = hass_data
        self.data = {}  # Aquí almacenaremos los últimos datos recibidos de cada tema

    async def async_setup(self):
        """Suscribe to the device MQTT topics tree."""
        await self.hass.components.mqtt.async_subscribe(self.settings["mqtt_topic"], self._received_message)

    async def _received_message(self, msg):
        """Función que se llama cuando se recibe un mensaje MQTT."""
        _LOGGER.info(f"Mensaje recibido en {msg.topic}: {msg.payload}")
        # Guardar el dato recibido
        self.data[msg.topic] = msg.payload
        # Actualizar el coordinador y notificar a las entidades
        self.async_set_updated_data(self.data)
