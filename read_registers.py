#!/usr/bin/env python
# -*- coding: utf-8 -*-

# read_register
# read 10 registers and print result on stdout

# you can use the tiny modbus server "mbserverd" to test this code
# mbserverd is here: https://github.com/sourceperl/mbserverd

# the command line modbus client mbtget can also be useful
# mbtget is here: https://github.com/sourceperl/mbtget

from pyModbusTCP.client import ModbusClient

SERVER_HOST = "192.168.181.76"
SERVER_PORT = 502

c = ModbusClient()

# uncomment this line to see debug message
c.debug(True)

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

# open or reconnect TCP to server
if not c.is_open():
    if not c.open():
        print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

# if open() is ok, read register (modbus function 0x03)
if c.is_open():
    # read 16 registers at address 0, store result in regs list
    regs = c.read_holding_registers(5408, 16)

    # if success display registers
    if regs:
        split_regs = list()

        # Run through reg list returned by read_holding registers, and split off
        # the 'XXXX' per register into 'XX' 'XX' by shifting and masking
        # then recombine them into a split_regs list
        for i, item in enumerate(regs):
            split_regs.append(regs[i] >> 8)
            split_regs.append(regs[i] & 0xff)

        # convert the split_regs list into its ASCII form
        ascii_list = [chr(c) for c in split_regs]

        # convert the split_regs list into a string
        s = ''.join(map(str,ascii_list))

        print(str(s))
