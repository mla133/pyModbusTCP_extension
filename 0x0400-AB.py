#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import time
import extmod  # updated modbus library that handles floats/doubles/text

# Define connection parameters
SERVER_HOST = "192.168.181.79"
SERVER_PORT = 502
c = extmod.ExtendedModbusClient(host=SERVER_HOST, port=SERVER_PORT, auto_open=True)

# uncomment this line to see debug message
#c.debug(True)

# open or reconnect TCP to server
if not c.is_open():
    if not c.open():
        print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

# if open() is ok 
if c.is_open():
    # Issue Command Data
    result = c.write_multiple_registers(0, [12, 0x0400, 2, 0, 64, 0, 0]) 
    if result:
        print("Command Packet sent")

    # Force 4096 to execute ExtSvcs, then read if command was sent OK
    update = c.write_single_coil(4096,1)
    if update:
        result = c.read_input_registers(0,4)
        print("Result: " + str(result))
        print("Return Code: " + hex(result[2]))
