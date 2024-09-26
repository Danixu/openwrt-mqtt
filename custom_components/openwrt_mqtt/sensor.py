from homeassistant.helpers.entity import Entity

from .constants import DOMAIN

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Does Nothing."""
    pass
    #coordinator = hass.data[DOMAIN][config_entry.entry_id]

    '''
    async def handle_sensor(sensor_id, entity_id, sensor_type, payload):
        """Añadir entidades dinámicamente y actualizar su estado."""
        sensor = coordinator.get_or_create_sensor(sensor_id, sensor_type)

        if sensor.hass is None:
            # Añadir entidad si no existe
            async_add_entities([sensor], True)

        # Actualizar el estado y atributos del sensor
        await sensor.async_update(
            payload.get("state"),
            {k: v for k, v in payload.items() if k not in ["id", "ent", "state", "type"]}
        )
        sensor.async_write_ha_state()
    '''



class BaseSensor(Entity):
    def __init__(self, child):
        super().__init__(self)  
        self._registered = False
        self._child = child

    def register_sensor(self):
        if not self._registered:
            async_add_entities([self._child], True)
            self._registered = True


class HumiditySensor(BaseSensor):
    """Clase para representar un sensor de humedad basado en MQTT."""

    def __init__(self, device_id, sensor_id):
        super().__init__(self)
        self._device_id = device_id
        self._sensor_id = sensor_id
        self._state = None
        self._attributes = {}
        self._registered = False

    @property
    def name(self):
        """Nombre del sensor."""
        return f"{self._device_id} - Humidity Sensor {self._sensor_id}"

    @property
    def state(self):
        """Estado del sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Atributos adicionales del sensor."""
        return self._attributes

    async def async_update(self, state, attributes):
        """Actualizar el estado y los atributos del sensor."""
        self._state = state
        self._attributes = attributes
        self.async_write_ha_state()

class TemperatureSensor(BaseSensor):
    """Clase para representar un sensor de temperatura basado en MQTT."""

    def __init__(self, device_id, sensor_id):
        self._device_id = device_id
        self._sensor_id = sensor_id
        self._state = None
        self._attributes = {}
        self._registered = False

    @property
    def name(self):
        """Nombre del sensor."""
        return f"{self._device_id} - Temperature Sensor {self._sensor_id}"

    @property
    def state(self):
        """Estado del sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Atributos adicionales del sensor."""
        return self._attributes

    async def async_update(self, state, attributes):
        """Actualizar el estado y los atributos del sensor."""
        self._state = state
        self._attributes = attributes
        self.async_write_ha_state()
