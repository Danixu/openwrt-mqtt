from datetime import timedelta
import logging
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt import async_subscribe

from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

class OpenWRTMqttCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry):
        super().__init__(
            hass,
            _LOGGER,
            name=f"{config_entry.data["id"]} Coortinator",
            update_interval=timedelta(minutes=1),  # Update it every minute
        )
        self.config_entry = config_entry
        self.devices = {}
        self._unsubscribe = None

        _LOGGER.setLevel(logging.DEBUG)

        # Subscribe to the topic
        hass.async_create_task(self.async_subscribe_to_topic(f"{config_entry.data["mqtt_topic"]}/#"))

    async def async_subscribe_to_topic(self, topic):
        """Función que maneja la suscripción y guarda la función de desuscripción."""
        # Esperar a que la suscripción termine y guardar el desuscriptor
        self._unsubscribe = await async_subscribe(self.hass, topic, self._received_message)

    async def async_unsubscribe_from_topic(self):
        """Desuscribirse si la función de desuscripción fue definida."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    async def _async_update_data(self):
        return self.devices


    def _determine_entity_device_group(self, entity_name):
        if re.match("cpu-[\\d]+", entity_name):
            return "processor"
        
        return None

    async def _received_message(self, msg):
        """
        Function called when MQTT message arrives.
        This function updates the devices and sensors in the coordinator if requried.
        """
        _LOGGER.info(f"Received message in {msg.topic}: {msg.payload}")
        # Extract the device type and the entity from the topic
        entity_found = re.match(".*\\/(.+)\\/(.+)$", msg.topic)

        if not entity_found:
            _LOGGER.debug("Unable to extract the data from the topic.")
        else:
            _LOGGER.debug(
                f"Detected a device {entity_found.groups()[0]} with an entity {entity_found.groups()[1]}"
            )

            # Get the device group to avoid to create a device by every cpu for example
            device_group = self._determine_entity_device_group(entity_found.groups()[0])
            if device_group == None:
                _LOGGER.debug("The device group for the device %s cannot be determined." % entity_found.groups()[0])
                return
            
            # Check if the group already exists and if not, create it
            if device_group not in self.devices:
                self.devices[device_group]= {}

            # Now just update the entity data:
            sensor_name = f"{entity_found.groups()[0]}_{entity_found.groups()[1]}"
            self.devices[device_group][sensor_name] = msg.payload
