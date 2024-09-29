from datetime import timedelta
import logging
import re

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.components.mqtt import async_subscribe

_LOGGER = logging.getLogger(__name__)

class coordinatorDevice():
    def __init__(self):
        self.registered = False
        self.entities = {}

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

        _LOGGER.setLevel(logging.DEBUG)

        hass.async_create_task(
            async_subscribe(hass, f"{config_entry.data["mqtt_topic"]}/#", self._received_message)
        )


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
            return
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
            if not device_group in self.devices:
                self.devices[device_group]= {}

            # Now just update the entity data:
            sensor_name = f"{entity_found.groups()[0]}_{entity_found.groups()[1]}"
            self.devices[device_group][sensor_name] = msg.payload
