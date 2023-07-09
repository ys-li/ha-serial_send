"""Platform for light integration."""
from __future__ import annotations
import asyncio

import logging
from typing import Any

import voluptuous as vol
from .serial_send import SERIAL_SCHEMA, DOMAIN, SerialSendInstance

from pprint import pformat

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.cover import (
    CoverEntity,
    PLATFORM_SCHEMA,
    STATE_OPENING,
    STATE_CLOSING,
    CoverEntityFeature,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

# This implementation is specific for a type of RF emitter that takes in serial command to continuously emit a certain signal, and stops when it receives another serial command.
# Therefore, this implementation is not meant for general use for all types of RF emitter.

CONF_SERIAL_CMD_START_OPEN = "serial_cmd_start_open"
CONF_SERIAL_CMD_END_OPEN = "serial_cmd_end_open"
CONF_SERIAL_INTERVAL = "serial_cmd_interval_ms"
CONF_SERIAL_CMD_START_CLOSE = "serial_cmd_start_close"
CONF_SERIAL_CMD_END_CLOSE = "serial_cmd_end_close"

_LOGGER = logging.getLogger(DOMAIN)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(SERIAL_SCHEMA)
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(
            CONF_SERIAL_CMD_START_OPEN
        ): cv.string,  # Serial command, in hex string, for starting to open this cover
        vol.Required(
            CONF_SERIAL_CMD_END_OPEN
        ): cv.string,  # Serial command, in hex string, for stopping opening this cover
        vol.Optional(
            CONF_SERIAL_INTERVAL
        ): cv.positive_int,  # Interval between sending the open command and the close command, in ms
        vol.Optional(
            CONF_SERIAL_CMD_START_CLOSE
        ): cv.string,  # Serial command, in hex string, for starting to close this cover
        vol.Optional(
            CONF_SERIAL_CMD_END_CLOSE
        ): cv.string,  # Serial command, in hex string, for ending closing this cover
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

    add_entities([SerialSendCover(config)])


class SerialSendCover(CoverEntity):
    """Representation of an generic cover. Stateless."""

    def __init__(self, config) -> None:
        """Initialize an GodoxLight."""
        _LOGGER.info(pformat(config))
        self._serial = SerialSendInstance(**config)
        self._serial_cmd_start_open = config[CONF_SERIAL_CMD_START_OPEN]
        self._serial_cmd_end_open = config[CONF_SERIAL_CMD_END_OPEN]
        self._serial_cmd_start_close = config[CONF_SERIAL_CMD_START_CLOSE]
        self._serial_cmd_end_close = config[CONF_SERIAL_CMD_END_CLOSE]
        self._serial_cmd_interval = config[CONF_SERIAL_INTERVAL]
        self._name = config[CONF_NAME]
        self._state = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def is_closed(self) -> bool | None:
        """This implementation does not support returning the state of the cover."""
        return None

    @property
    def is_closing(self) -> bool:
        return self._state == STATE_CLOSING

    @property
    def is_opening(self) -> bool:
        return self._state == STATE_OPENING

    @property
    def supported_features(self) -> CoverEntityFeature:
        return (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        self._state = STATE_OPENING
        self._serial.send_cmd(self._serial_cmd_start_open)
        self._serial.set_is_busy(True)
        await asyncio.sleep(self._serial_cmd_interval / 1000)
        # check if the cover is still opening, it can be stopped via the stop function
        if self._state == STATE_OPENING:
            self._state = None
            self._serial.set_is_busy(False)
            self._serial.send_cmd(self._serial_cmd_end_open)

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        self._state = STATE_CLOSING
        self._serial.send_cmd(self._serial_cmd_start_close)
        self._serial.set_is_busy(True)
        await asyncio.sleep(self._serial_cmd_interval / 1000)
        if self._state == STATE_CLOSING:
            self._state = None
            self._serial.set_is_busy(False)
            self._serial.send_cmd(self._serial_cmd_end_close)

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        if self._state == STATE_CLOSING:
            self._state = None
            self._serial.set_is_busy(False)
            self._serial.send_cmd(self._serial_cmd_end_close)
        else:
            self._state = None
            self._serial.set_is_busy(False)
            self._serial.send_cmd(self._serial_cmd_end_open)
