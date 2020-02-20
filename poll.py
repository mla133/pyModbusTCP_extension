#importing all needed libraries
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import datetime
import csv
import time
import extmod  # updated modbus library that handles floats/doubles/text

SERVER_HOST = "192.168.181.79"
SERVER_PORT = 502
LOGFILE     = "injector_data_021120.csv"

c = extmod.ExtendedModbusClient()

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

print("BatchGV\t\tAdditive Rates\t\t");

# Add Header to top of CSV file
with open(LOGFILE, 'a') as inj_data:
    inj_data_writer = csv.writer(inj_data)
    inj_data_writer.writerow(['Time', 'Trans#', 'Batch#', 'Recipe#', 'Trans GV', 'Add5 #inj', 'Add5 Rate', 'Add5_Vol','Add7 #inj', 'Add7 Rate', 'Add7_Vol'])
inj_data.close()

while True:
    # open or reconnect TCP to server
    if not c.is_open():
        if not c.open():
            print("unable to connect to "+SERVER_HOST+":"+str(SERVER_PORT))

    # if open() is ok, read info
    if c.is_open():
        trans_no    = c.read_input_registers(4864,1)
        batch_no    = c.read_input_registers(7683,1)
        recipe_no   = c.read_input_registers(7681,1)

        add5_volinj = c.read_float(4, 3128, 1)
        add6_volinj = c.read_float(4, 3130, 1)
        add7_volinj = c.read_float(4, 3132, 1)

        add5_curinj = c.read_input_registers(3652, 1)
        add6_curinj = c.read_input_registers(3653, 1)
        add7_curinj = c.read_input_registers(3654, 1)

        add5_rate   = c.read_float(4, 3080, 1)
        add6_rate   = c.read_float(4, 3082, 1)
        add7_rate   = c.read_float(4, 3084, 1)

        R7_add5_rate = c.read_float(3, 10872, 1)
        R7_add6_rate = c.read_float(3, 10874, 1)
        R7_add7_rate = c.read_float(3, 10876, 1)

        R11_add5_rate = c.read_float(3, 11896, 1)
        R11_add6_rate = c.read_float(3, 11898, 1)
        R11_add7_rate = c.read_float(3, 11900, 1)

        add5_vol    = c.read_double(4, 4520, 1)
        add6_vol    = c.read_double(4, 4524, 1)
        add7_vol    = c.read_double(4, 4528, 1)

        AL3time = c.read_text(3, 3728, 16)
        trans_GV    = c.read_double(4, 4484, 1)

        print(str(trans_no)+str(batch_no)+str(recipe_no) + "\t" + str(trans_GV) + "\t" + str(add5_rate) + str(add7_rate) + "\t" + str(R11_add5_rate) + str(R11_add7_rate) + "\t" + str(add5_vol) + str(add7_vol))

        c.close()

        with open(LOGFILE, 'a') as inj_data:
            inj_data_writer = csv.writer(inj_data)
            inj_data_writer.writerow([AL3time, trans_no, batch_no, recipe_no, trans_GV, add5_curinj, add5_rate, add5_vol, add7_curinj, add7_rate, add7_vol])
        inj_data.close()

        # sleep 1s before next polling
        time.sleep(0.1)
    else:
        #letting the user know that the device isn't connected
        print("Device not connected")
