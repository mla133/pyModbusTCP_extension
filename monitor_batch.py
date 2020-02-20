#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyModbusTCP.client import ModbusClient
import time
import struct
import datetime
import csv
import time

import extmod  # updated modbus library that handles floats/doubles/text

LOGFILE     = "02182020-run2.csv"
SERVER_HOST = "192.168.181.79"
SERVER_PORT = 502

c = extmod.ExtendedModbusClient(host=SERVER_HOST, port=SERVER_PORT, auto_open=True)

# uncomment this line to see debug message
#c.debug(True)

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

# open or reconnect TCP to server
if not c.is_open():
    if not c.open():
        print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))


# Check for alarms from possible previous run, stop if encountered 
status      = c.read_discrete_inputs(4160, 17)
if status[8]:
    print("Alarms are present...check AccuLoad.")
    exit() 

# 0x0400 AB variant, allocate recipe 7 for the batch
command = c.write_multiple_registers(0, [12, 0x0400, 2, 0, 64, 0, 0]) 
update = c.write_single_coil(4096,1)
AB_result = c.read_input_registers(0, 4)
print("Allocated Recipe 7")
print(str(hex(AB_result[2])))

# 0x0400 SB variant, set batch to 1010101010101010101000 gallons
# Issue Command Data
command = c.write_multiple_registers(0, [12, 0x0400, 3])
command = c.write_float(3, [1000.0])
command = c.write_single_register(5, 0xFFFF)
command = c.write_single_register(6, 0xFFFF)
update = c.write_single_coil(4096,1)
SB_result = c.read_input_registers(0, 4)
print("Setting batch volumes...")
print(str(hex(SB_result[2])))

# 0x0400 SA variant, start batch...
command = c.write_multiple_registers(0, [4, 0x0400, 6])
update = c.write_single_coil(4096,1)
SA_result = c.read_input_registers(0, 4)
print("Starting Batch...")
print(str(hex(SA_result[2])))

time.sleep(1)
print("Running Batch...")

# Enter polling loop to monitor injectors, break when batch is done...
while True:
    # open or reconnect TCP to server
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

    # if open() is ok, read coils (modbus function 0x01)
    if c.is_open():
        # read Transaction Info Inputs (watching for batch running/done)
        status      = c.read_discrete_inputs(4160, 17)
        trans_no    = c.read_input_registers(4864,1)
        batch_no    = c.read_input_registers(7683,1)
        recipe_no   = c.read_input_registers(7681,1)
        add5_volinj = c.read_float(4, 3128, 1)
        add5_curinj = c.read_input_registers(3652, 1)
        add5_rate   = c.read_float(4, 3080, 1)
        add5_vol    = c.read_double(4, 4520, 1)
        AL3time     = c.read_text(3, 3728, 16)
        trans_GV    = c.read_double(4, 4484, 1)
        
        # check for alarms, if any, bail and notify user
        if status[8]:
            print("ALARM occurred...check AccuLoad.")
            break

        # check for BD flag and NOT FL flag to then break to end transaction
        if (status[3] and not status[12]):
            print("Batch Done...")
            break

        with open(LOGFILE, 'a') as inj_data:
            inj_data_writer = csv.writer(inj_data)
            inj_data_writer.writerow([AL3time, trans_no, batch_no, recipe_no, status[2], status[3], status[4], status[12], trans_GV, add5_curinj, add5_rate, add5_vol])
        inj_data.close()

    # sleep 0.5s before next polling
    time.sleep(0.5)

# 0x0400 EB variant, end transaction...
command = c.write_multiple_registers(0, [4, 0x0400, 4])
update = c.write_single_coil(4096,1)
EB_result = c.read_input_registers(0, 4)
print("Ending Batch...")
print(str(hex(EB_result[2])))

# 0x0400 ET variant, end transaction...
command = c.write_multiple_registers(0, [4, 0x0400, 5])
update = c.write_single_coil(4096,1)
ET_result = c.read_input_registers(0, 4)
print("Ending Transaction...")
print(str(hex(ET_result[2])))
