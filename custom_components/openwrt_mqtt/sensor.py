import logging

from homeassistant.helpers.entity import Entity, EntityCategory
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
        _LOGGER.debug("Updating entities")
        
        # Iterate over the devices and sensor in the coordinator
        for device_name, sensors in coordinator.devices.items():
            for sensor_name, sensor_data in sensors.items():
                unique_id = f"{entry.data['id']}_{device_name}_{sensor_name}"
                
                # Verificar si la entidad ya existe
                if unique_id not in hass.data[DOMAIN]["entities"]:
                    name = sensor_data["sensor_data"]["name"]
                    entity = None
                    if device_name == "processor":
                        name = name.format(sensor_data["extracted_data"][0].upper())

                    if sensor_data["sensor_data"]["sensor_type"] == "percent":
                        entity = PercentEntity(coordinator, entry, sensor_data, name)
                    hass.data[DOMAIN]["entities"][unique_id] = entity
                    new_entities.append(entity)

        # Add the new entities to Home Assistant if there is any new
        if new_entities:
            _LOGGER.debug("There are new entities. Creating it...")
            async_add_entities(new_entities.copy())

    # Execute the first update
    await entities_update()

    # Dynamically update when the coordinator is updated
    coordinator.async_add_listener(lambda: hass.async_create_task(entities_update()))

class PercentEntity(Entity):
    _attr_unit_of_measurement = "%"
    def __init__(self, coordinador, entry, sensor_data, name):
        self.coordinador = coordinador
        self.entry = entry
        self.sensor_data = sensor_data

        self._attr_entity_registry_enabled_default = self.sensor_data["sensor_data"].get("enabled_default", False)
        self._attr_name = name
        self._attr_icon = self.sensor_data["sensor_data"]["icon"]
        self._attr_unique_id = f"{self.entry.data['id']}_{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        if self.sensor_data["sensor_data"].get("diagnostic", False):
            _attr_entity_category = EntityCategory.DIAGNOSTIC
        else:
            _attr_entity_category = None
        self._state = None

    @property
    def state(self):
        # Get the current state from the coordinator
        sensor_id = f"{self.sensor_data["extracted_data"][0]}_{self.sensor_data["extracted_data"][1]}"
        _LOGGER.debug("Getting the state of the sensor %s", sensor_id)
        value = None
        try:
            value = float(self.coordinador.devices[self.sensor_data["device_group"]][sensor_id]["value"].split(":")[1])
            value = round(value, 2)

        except Exception as e:
            _LOGGER.warning("The sensor %s value cannot be converted to float: %s", self._attr_name, e)
        
        _LOGGER.debug("Value: %f", value)
        return value

    async def async_update(self):
        # Request a data update to the coordinator
        await self.coordinador.async_request_refresh()

    @property
    def device_info(self):
        device_info = {
            "identifiers": {(DOMAIN, self.entry.entry_id)},
            "name": f"{self.entry.data['id']}: {self.sensor_data["device_group"].capitalize()}",
            "manufacturer": "OpenWRT",
        }
        _LOGGER.debug(f"Device Info: {device_info}")
        return device_info