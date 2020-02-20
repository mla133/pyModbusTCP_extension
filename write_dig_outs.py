#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Toggle Digital Outputs 

from pyModbusTCP.client import ModbusClient
import time

SERVER_HOST = "192.168.181.76"
SERVER_PORT = 502

c = ModbusClient()

# uncomment this line to see debug message
#c.debug(True)

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

# open or reconnect TCP to server
if not c.is_open():
    if not c.open():
        print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

# open or reconnect TCP to server
if not c.is_open():
    if not c.open():
        print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

while True:
    # if open() is ok, read coils (modbus function 0x01)
    if c.is_open():
        # read System Status(func 02, result 4096-4106)
        result = c.read_holding_registers(2106, 1)
        # if success display registers
        if result:
            print("PI (float): " + str(result))
            time.sleep(1)
