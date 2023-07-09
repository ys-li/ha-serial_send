"""Utilities for sending serial"""

import asyncio
import logging
import serial
import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_VALUE_TEMPLATE
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError


### Base configs for entities to base on

DOMAIN = "serial_send"
LOGGER = logging.getLogger(DOMAIN)

CONF_SERIAL_PORT = "serial_port"
CONF_BAUDRATE = "baudrate"
CONF_BYTESIZE = "bytesize"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"
CONF_XONXOFF = "xonxoff"
CONF_RTSCTS = "rtscts"
CONF_DSRDTR = "dsrdtr"

DEFAULT_NAME = "Serial Sensor"
DEFAULT_BAUDRATE = 9600
DEFAULT_BYTESIZE = serial.EIGHTBITS
DEFAULT_PARITY = serial.PARITY_NONE
DEFAULT_STOPBITS = serial.STOPBITS_ONE
DEFAULT_XONXOFF = False
DEFAULT_RTSCTS = False
DEFAULT_DSRDTR = False

# Validation of the user's configuration
SERIAL_SCHEMA = {
    vol.Required(CONF_SERIAL_PORT): cv.string,
    vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): cv.positive_int,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template,
    vol.Optional(CONF_BYTESIZE, default=DEFAULT_BYTESIZE): vol.In(
        [
            serial.FIVEBITS,
            serial.SIXBITS,
            serial.SEVENBITS,
            serial.EIGHTBITS,
        ]
    ),
    vol.Optional(CONF_PARITY, default=DEFAULT_PARITY): vol.In(
        [
            serial.PARITY_NONE,
            serial.PARITY_EVEN,
            serial.PARITY_ODD,
            serial.PARITY_MARK,
            serial.PARITY_SPACE,
        ]
    ),
    vol.Optional(CONF_STOPBITS, default=DEFAULT_STOPBITS): vol.In(
        [
            serial.STOPBITS_ONE,
            serial.STOPBITS_ONE_POINT_FIVE,
            serial.STOPBITS_TWO,
        ]
    ),
    vol.Optional(CONF_XONXOFF, default=DEFAULT_XONXOFF): cv.boolean,
    vol.Optional(CONF_RTSCTS, default=DEFAULT_RTSCTS): cv.boolean,
    vol.Optional(CONF_DSRDTR, default=DEFAULT_DSRDTR): cv.boolean,
}

serial_instances = {}  # for holding singletons instances of serial ports\


class SerialSendInstance:
    """
    Instance for controlling serial port
    """

    def __new__(cls, *args, **kwargs):
        """
        Create singleton instances for each port.
        For blocking actions on serial ports that are in use.
        """
        serial_port = kwargs["serial_port"]
        if serial_port not in serial_instances:
            cls.instance = super(SerialSendInstance, cls).__new__(cls)
            serial_instances[serial_port] = cls.instance
        return cls.instance

    def __init__(
        self,
        serial_port: str,
        baudrate: int = 9600,
        bytesize: int = 8,
        parity: str = "N",
        stopbits: int = 1,
        timeout: int = None,
        xonxoff: bool = False,
        rtscts: bool = False,
        **kwargs,
    ) -> None:
        """Create a instance of serial controller

        Args:
            serial_port (str): The path for the serial port
            baudrate (int, optional): BDefaults to 9600.
            bytesize (int, optional): Defaults to 8.
            parity (str, optional): Defaults to 'N'.
            stopbits (int, optional): Defaults to 1.
            timeout (int, optional): Defaults to None.
            xonxoff (bool, optional): Defaults to False.
            rtscts (bool, optional): Defaults to False.
        """
        self._serial_port = serial_port

        _serial = serial.Serial()
        _serial.baudrate = baudrate
        _serial.bytesize = bytesize
        _serial.parity = parity
        _serial.stopbits = stopbits
        _serial.timeout = timeout
        _serial.xonxoff = xonxoff
        _serial.rtscts = rtscts
        self._serial = _serial
        self.is_busy = False

    def open_port(self) -> bool:
        """Opens the serial port with params as specified in the constructor

        Returns:
            bool: Whether the serial port is opened
        """
        LOGGER.debug(
            "OPENING SERIAL PORT to %s, is_open = %s",
            self._serial.port,
            self._serial.is_open,
        )
        self._serial.open()
        LOGGER.debug("OPENED SERIAL PORT, is_open = %s", self._serial.is_open)
        return self._serial.is_open

    def close_port(self) -> bool:
        """Close the serial port.

        Returns:
            bool: Whether the serial port has been successfully closed.
        """
        LOGGER.debug(
            "CLOSING SERIAL PORT to %s, is_open = %s",
            self._serial.port,
            self._serial.is_open,
        )
        self._serial.close()
        LOGGER.debug("CLOSED SERIAL PORT, is_open = %s", self._serial.is_open)
        return not self._serial.is_open

    def set_is_busy(self, is_busy: bool):
        self.is_busy = is_busy

    def send_cmd(self, cmd_hex_str: str) -> bool:
        """Sends the command via the serial port

        Args:
            cmd_hex_str (str): The byte string in str. Will be parsed in the function
        """
        if self.is_busy:
            False

        if not self._serial.is_open:
            self._serial.port = self._serial_port
            self.open_port()

        command = bytes.fromhex(cmd_hex_str)
        bytes_wrote = self._serial.write(command)

        LOGGER.debug(
            "WRITTEN TO SERIAL PORT %s BYTES %s, BYTE %s",
            self._serial.port,
            bytes_wrote,
            "".join("{:02x} ".format(x) for x in command),
        )

        return True
