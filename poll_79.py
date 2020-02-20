#importing all needed libraries
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import datetime
import csv
import time

################################################################################################################
#    functions to decode double and float values
################################################################################################################

#########################
# floating-point function
#########################
def decode_ieee(val_int):
   return struct.unpack("f", struct.pack("I", val_int))[0]

def decode_ieee_double(val_int):
   return struct.unpack("d", struct.pack("q", val_int))[0]

#################################################################
# decoding long long (64 bits)
#################################################################


def word_list_to_longlong(val_list, big_endian=True):
   # allocate list for long int
    longlong_list = [None] * int(len(val_list) / 4)
    # fill registers list with register items
    for i, item in enumerate(longlong_list):
        if big_endian:
           longlong_list [i] = (val_list[i * 4] << 48) + (val_list[(i * 4) + 1] << 32) + (val_list[(i * 4) + 2] << 16) + val_list[(i * 4) + 3]
        else:
            longlong_list [i] = (val_list[(i * 4) + 3] << 48) + (val_list[(i * 4) + 2] << 32) + (val_list[(i * 4) + 1] << 16) + val_list[i * 4]
    # return longlong_list list
    return longlong_list


def long_list_to_word(val_list, big_endian=True):
   # allocate list for long int
    word_list = list()
    # fill registers list with register items
    for i, item in enumerate(val_list):
        if big_endian:
            word_list.append(val_list[i] >> 16)
            word_list.append(val_list[i] & 0xffff)
        else:
            word_list.append(val_list[i] & 0xffff)
            word_list.append(val_list[i] >> 16)
    # return long list
    return word_list

#################################################################################################################################
#                End of data decoding functions
#################################################################################################################################

class ExtendedModbusClient(ModbusClient):
    def read_float(self, reg_type,  address, number=1):
        if reg_type == 4:
            reg_l = self.read_input_registers(address, number * 2)
        else:
            reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [utils.decode_ieee(f) for f in utils.word_list_to_long(reg_l)]
        else:
            return None

    def write_float(self, address, floats_list):
        b32_l = [utils.encode_ieee(f) for f in floats_list]
        b16_l = utils.long_list_to_word(b32_l)
        return self.write_multiple_registers(address, b16_l)

    def read_double(self, reg_type, address, number=1):
        if reg_type == 4:
            reg_ll = self.read_input_registers(address, number * 4)
        else:
            reg_ll = self.read_holding_registers(address, number * 4)
        if reg_ll:
            return [decode_ieee_double(d) for d in word_list_to_longlong(reg_ll)]
        else:
            return None
    def read_long(self, reg_type,  address, number=1):
        if reg_type == 4:
            reg_l = self.read_input_registers(address, number * 2)
        else:
            reg_l = self.read_holding_registers(address, number * 2)
        if reg_l:
            return [utils.word_list_to_long(reg_l)]
        else:
            return None

    def read_text(self, reg_type, address, number=1):
        if reg_type == 4:
            reg_t = self.read_input_registers(address, number)
        else:
            reg_t = self.read_holding_registers(address, number)
        if reg_t:
            split_regs = list()

            # Run through reg list returned by read_holding registers, and split off
            # the 'XXXX' per register into 'XX' 'XX' by shifting and masking
            # then recombine them into a split_regs list
            for i, item in enumerate(reg_t):
                split_regs.append(reg_t[i] >> 8)
                split_regs.append(reg_t[i] & 0xff)

            # convert the split_regs list into its ASCII form
            ascii_list = [chr(c) for c in split_regs]

            # convert the split_regs list into a string
            s = ''.join(map(str,ascii_list))
            return(s)
        else:
            return None

       
#    #opening and naming the csv file so it can be written to
#    with open('device_data.csv','a') as device_data:
#        device_data_writer = csv.writer(device_data)
#        #giving each of the columns a heading
#        device_data_writer.writerow(['   ', 'MicroFlow', 'AccuLoad', 'UCOS Windows', 'UCOS Linux','Omni', 'Spirit'])
#        #adding the date from each device to each column
#        device_data_writer.writerow(['Date', MicroDate, ALDate, windDate, linDate, OMNIDate, SpiritDate])
#        #adding the time from each device to each column
#        device_data_writer.writerow(['Time', MicroTime, ALTime, windTime, linTime, OMNITime, SpiritTime])
#        #assigning IV values to each column 
#        device_data_writer.writerow(['IV', MicroIV, AccuIV, windIV, linIV, OmniIV, SpiritIV])
#        #assigning GV values to each column
#        device_data_writer.writerow(['GV', MicroGV, AccuGV, windGV, linGV, OmniGV, SpiritGV])
#        #assigning GST values to each column
#        device_data_writer.writerow(['GST', MicroGST, AccuGST, windGST, linGST, OmniGST, SpiritGST])
#        #assigning GSV values to each column
#        device_data_writer.writerow(['GSV', MicroGSV, AccuGSV, windGSV, linGSV, OmniGSV, SpiritGSV])
#        #assigning NSV values to each column
#        device_data_writer.writerow(['NSV', MicroNSV, AccuNSV, windNSV, linNSV, OmniNSV, SpiritNSV])
#        #assigning CTL values to each column
#        device_data_writer.writerow(['CTL', MicroCTL, AccuCTL, windCTL, linCTL, OMNICTL, SpiritCTL])
#        #assigning CPL values to each column
#        device_data_writer.writerow(['CPL', MicroCPL, AccuCPL, windCPL, linCPL, OMNICPL, SpiritCPL])
#        #assigning CTPL values to each column
#        device_data_writer.writerow(['CTPL', MicroCTPL, AccuCTPL, windCTPL, linCTPL, OMNICTPL, SpiritCTPL])
#        #assigning ref temp to each column
#        device_data_writer.writerow(['Ref. Temp.', MicroRefTemp, AccuRefTemp, windRefTemp, linRefTemp, OMNIRefTemp, SpiritRefTemp])
#        #assigning maintainence temp to each column
#        device_data_writer.writerow(['Main. Temp.', MicroMainTemp, AccuMainTemp, windMainTemp, linMainTemp, OMNIMainTemp, SpiritMainTemp])
#        #assigning Live temp to each column
#        device_data_writer.writerow(['Live Temp.', MicroLiveTemp, AccuLiveTemp, windLiveTemp, linLiveTemp, OMNILiveTemp, SpiritLiveTemp])
#        #assigning average temp to each column
#        device_data_writer.writerow(['Avg. Temp.', MicroAvgTemp, AccuAvgTemp, windAvgTemp, linAvgTemp, OMNIAvgTemp, SpiritAvgTemp])
#        #assigning maintainence pressure to each column
#        device_data_writer.writerow(['Main. Pressure', MicroMainPres, AccuMainPres, windMainPres, linMainPres, OMNIMainPres, SpiritMainPres])
#        #assigning average pressure to each column
#        device_data_writer.writerow(['Avg. Pressure', MicroAvgPres, AccuAvgPres, windAvgPres, linAvgPres, OMNIAvgPres, SpiritAvgPres])
#        #assigning live pressure to each column
#        device_data_writer.writerow(['Live Pressure', MicroLivePres, AccuLivePres, windLivePres, linLivePres, OMNILivePres, SpiritLivePres])
#        #assigning reference density to each column
#        device_data_writer.writerow(['Ref. Density', MicroRefDens, AccuRefDens, windRefDens, linRefDens, OMNIRefDens, SpiritRefDens])
#        #assigning average density to each column
#        device_data_writer.writerow(['Avg. Density', MicroAvgDens, AccuAvgDens, windAvgDens, linAvgDens, OMNIAvgDens, SpiritAvgDens])
#        #assigning live density to each column
#        device_data_writer.writerow(['Live Density', MicroLiveDens, AccuLiveDens, windLiveDens, linLiveDens, OMNILiveDens, SpiritLiveDens])
#        #assigning k factor to each column
#        device_data_writer.writerow(['K Factor', MicroKfactor, AccuKfactor, windkfactor, linkfactor, OMNIKfactor, SpiritKfactor])
#        #assigning meter factor to each column
#        device_data_writer.writerow(['Meter Factor', Micrometerfactor, Accumeterfactor, windmeterfactor, linmeterfactor, OMNImeterfactor, Spiritmeterfactor])
#        #assigning bs&w
#        device_data_writer.writerow(['BS&W', MicroBSW, AccuBSW, windBSW, linBSW, OMNIBSW, SpiritBSW])
#        #assigning mass to each column
#        device_data_writer.writerow(['Mass', Micromass, Accumass, windmass, linmass, OMNImass, Spiritmass])
#        #assigning pulse total to each column
#        device_data_writer.writerow(['Pulse Total', Micropulse, Accupulse, windpulse, linpulse, OMNIpulse, Spiritpulse])
#   #closing the csv file     
#    device_data.close()

#########################################################################################################################

SERVER_HOST = "192.168.181.79"
SERVER_PORT = 502

c = ExtendedModbusClient()

# define modbus server host, port
c.host(SERVER_HOST)
c.port(SERVER_PORT)

print("BatchGV\t\tAdditive Rates\t\t");

# Add Header to top of CSV file
with open('injector_data.csv', 'a') as inj_data:
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

        with open('injector_data.csv', 'a') as inj_data:
            inj_data_writer = csv.writer(inj_data)
            inj_data_writer.writerow([AL3time, trans_no, batch_no, recipe_no, trans_GV, add5_curinj, add5_rate, add5_vol, add7_curinj, add7_rate, add7_vol])
        inj_data.close()

        # sleep 1s before next polling
        time.sleep(0.1)
    else:
        #letting the user know that the device isn't connected
        print("Device not connected")
