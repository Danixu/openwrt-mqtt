from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .constants import DOMAIN

import logging
import re
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required('id'): cv.string,
    vol.Required('mqtt_topic'): cv.string,
})


class OpenWrtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):

    async def async_step_reauth(self, user_input):
        return await self.async_step_user(user_input)

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )
        _LOGGER.debug(f"Input: {user_input}")

        title = f"{user_input["id"]}"
        # Verify if an entry with the same ID exists.
        for entry in self.hass.config_entries.async_entries('openwrt_mqtt'):
            if entry.data['id'] == user_input['id']:
                return self.async_abort(reason=f"The device ID {user_input['id']} already exists.")
            
        return self.async_create_entry(title=title, data=user_input)
    
    async def async_step_mqtt(self, discovery_info):
        """Handle discovery from MQTT."""
        _LOGGER.debug("Received MQTT discovery info: %s", discovery_info)

        topic_data = re.match("^(openwrt\\/([\\w\\s\\-]+))\\/.*$", discovery_info.topic)

        user_input = {
            'id': topic_data.groups()[1],
            'mqtt_topic': topic_data.groups()[0],
        }
        # Verifica si ya existe una entrada con este ID
        for entry in self.hass.config_entries.async_entries('openwrt_mqtt'):
            if entry.data['id'] == user_input["id"]:
                return self.async_abort(reason="Device already configured")

        return await self.async_step_user(user_input=user_input)