# Simple Serial Send Interface
A Home Assistant custom integration meant for sending commands to devices via serial ports.

## Why
I wrote this integration mainly to interface HASS with my old RF remote controlled lights and curtains. I have a microcontroller that takes in specific serial commands and emit RF remote signals accordingly. Feel free to try making this work for your use. Hope this repo makes that a tiny bit easier.

Entities implemented currently includes:
- **Light** 
- **Cover**

Does not track the state currently.

## Configuration file
```yaml
light:
  - platform: serial_send
    name: "Test light"
    serial_port: "/dev/pts/6" # path to the serial port
    serial_cmd_turn_on: "68 65 6C 6C 6F" # Hexadecimal representation of the command to send on turning on the entity, can be space delimited
    serial_cmd_turn_off: "62 79 65" # Hexadecimal representation of the command to send on turning off the entity, can be space delimited

cover:
  - platform: serial_send
    name: "Test cover"
    serial_port: "/dev/pts/6"
    serial_cmd_start_open: "5B 73 74 61 72 74 5F 6F 70 65 6E 5D" # Command to initiate opening the cover
    serial_cmd_end_open: "5B 65 6E 64 5F 6F 70 65 6E 5D" # Command to stop opening the cover
    serial_cmd_interval_ms: 3000 # Interval (in milliseconds) between sending the two commands
    serial_cmd_start_close: "5B 73 74 61 72 74 5F 63 6C 6F 73 65 5D"
    serial_cmd_end_close: "5B 65 6E 64 5F 63 6C 6F 73 65 5D"
```