from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class MiCoordinadorDeDatos(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, config_entry):
        super().__init__(
            hass,
            _LOGGER,
            name="Mi Coordinador de Datos",
            update_interval=timedelta(minutes=1),  # Actualización cada minuto
        )
        self.config_entry = config_entry
        self.devices = {}

    async def _async_update_data(self):
        # Simular la recepción de datos dinámicos
        nuevos_datos = await self.obtener_datos_dinamicos()
        
        # Actualizar el estado de dispositivos y sensores
        for device_name, device_data in nuevos_datos.items():
            if device_name not in self.devices:
                self.devices[device_name] = {}
            
            for sensor_name, sensor_value in device_data.items():
                self.devices[device_name][sensor_name] = sensor_value

        return self.devices

    async def obtener_datos_dinamicos(self):
        # Simular la obtención de datos
        return {
            "dispositivo_1": {
                "sensor_1": 42,
                "sensor_2": 75,
            },
            "dispositivo_2": {
                "sensor_1": 18,
                "sensor_3": 23,
            },
        }
