import logging

from homeassistant.helpers.entity import Entity
from .constants import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _LOGGER.setLevel(logging.DEBUG)

    # Create a container for the entities if it doesn't exists.
    if "entities" not in hass.data[DOMAIN]:
        hass.data[DOMAIN]["entities"] = {}

    # Function to dynamically update the entities.
    async def entities_update():
        new_entities = []
        _LOGGER.debug(entry.data)
        
        # Iterate over the devices and sensor in the coordinator
        for device_name, sensors in coordinator.devices.items():
            for sensor_name in sensors:
                unique_id = f"{entry.data['id']}_{device_name}_{sensor_name}"
                
                # Verificar si la entidad ya existe
                if unique_id not in hass.data[DOMAIN]["entities"]:
                    entity = MyEntity(coordinator, entry, device_name, sensor_name)
                    hass.data[DOMAIN]["entities"][unique_id] = entity
                    new_entities.append(entity)

        # Add the new entities to Home Assistant if there is any new
        if new_entities:
            async_add_entities(new_entities)

    # Execute the first update
    await entities_update()

    # Dynamically update when the coordinator is updated
    coordinator.async_add_listener(lambda: hass.async_create_task(entities_update()))

class MyEntity(Entity):
    def __init__(self, coordinador, entry, device_name, sensor_name):
        self.coordinador = coordinador
        self.entry = entry
        self.device_name = device_name
        self.sensor_name = sensor_name
        self._state = None

    @property
    def name(self):
        return f"{self.device_name} {self.sensor_name}"

    @property
    def unique_id(self):
        return f"{self.entry.data['id']}_{self.device_name}_{self.sensor_name}"

    @property
    def state(self):
        # Get the current state from the coordinator
        return self.coordinador.devices[self.device_name][self.sensor_name]

    async def async_update(self):
        # Request a data update to the coordinator
        await self.coordinador.async_request_refresh()

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"{self.entry.data['id']}: {self.device_name}",
            "manufacturer": "OpenWRT",
        }
        _LOGGER.debug(f"Device Info: {device_info}")
        return device_info

    @property
    def icon(self):
        return "mdi:chip"