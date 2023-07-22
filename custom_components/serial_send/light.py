"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from .serial_send import SERIAL_SCHEMA, DOMAIN, SerialSendInstance

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import LightEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

CONF_SERIAL_CMD_TURN_ON = "serial_cmd_turn_on"
CONF_SERIAL_CMD_TURN_OFF = "serial_cmd_turn_off"

_LOGGER = logging.getLogger(DOMAIN)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SERIAL_SCHEMA)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(
            CONF_SERIAL_CMD_TURN_ON
        ): cv.string,  # Serial command, in hex string, for turning on this light
        vol.Required(
            CONF_SERIAL_CMD_TURN_OFF
        ): cv.string,  # Serial command, in hex string, for turning off this light
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Godox Light platform."""
    # Add devices
    _LOGGER.info(pformat(config))

    add_entities([SerialSendLight(config)])


class SerialSendLight(LightEntity):
    """Representation of a generic light controlled by serial. Stateless."""

    def __init__(self, config) -> None:
        """Initialize an GodoxLight."""
        _LOGGER.info(pformat(config))
        self._serial = SerialSendInstance(**config)
        self._serial_cmd_turn_on = config[CONF_SERIAL_CMD_TURN_ON]
        self._serial_cmd_turn_off = config[CONF_SERIAL_CMD_TURN_OFF]
        self._name = config[CONF_NAME]
        self._is_on = False
        
    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._serial_cmd_turn_on.replace(" ", "") # use open command as the unique_id
    
    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._is_on

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._serial.send_cmd(self._serial_cmd_turn_on)
        self._is_on = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._serial.send_cmd(self._serial_cmd_turn_off)
        self._is_on = False