#importing all needed libraries
from pyModbusTCP.client import ModbusClient
from pyModbusTCP import utils
import struct
import datetime
import csv

################################################################################################################
#    functions to decode double and float values
################################################################################################################

#########################
# floating-point function
#########################
def decode_ieee(val_int):
    """Decode Python int (32 bits integer) as an IEEE single precision format

        Support NaN.

        :param val_int: a 32 bit integer as an int Python value
        :type val_int: int
        :returns: float result
        :rtype: float
    """
    return struct.unpack("f", struct.pack("I", val_int))[0]

def decode_ieee_double(val_int):
    """Decode Python int (64 bits integer) as an IEEE double precision format

        Support NaN.

        :param val_int: a 64 bit integer as an int Python value
        :type val_int: int
        :returns: double result
        :rtype: double
    """
    return struct.unpack("d", struct.pack("q", val_int))[0]

#################################################################
# decoding long long (64 bits)
#################################################################


def word_list_to_longlong(val_list, big_endian=True):
    """Word list (16 bits int) to long list (64 bits int)

        By default word_list_to_long() use big endian order. For use little endian, set
        big_endian param to False.

        :param val_list: list of 16 bits int value
        :type val_list: list
        :param big_endian: True for big endian/False for little (optional)
        :type big_endian: bool
        :returns: list of 64 bits int value
        :rtype: list
    """
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
    """Long list (32 bits int) to word list (16 bits int)

        By default long_list_to_word() use big endian order. For use little endian, set
        big_endian param to False.

        :param val_list: list of 32 bits int value
        :type val_list: list
        :param big_endian: True for big endian/False for little (optional)
        :type big_endian: bool
        :returns: list of 16 bits int value
        :rtype: list
    """
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

class FloatModbusClient(ModbusClient):
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
 
############################################################
# FROM HERE YOU CAN POLL/WRITE TO REGISTERS AS YOU SEE FIT #
############################################################

#prompting the user to enter the ip for each device
ip1 = input("Enter MicroFlow ip address (Press enter if MicroFlow is unused): ")
ip2 = input("Enter AccuLoad ip address (Press enter if AccuLoad is unused): ")
ip3 = input("Enter UCOS ip address (Press enter if UCOS is unused): ")
ip4 = input("Enter Omni ip address (Press enter if Omni is unused): ")
ip5 = input("Enter Spirit ip address (Press enter if Spirit is unused): ")

#declaring currentDT to equal the datetime function
currentDT = datetime.datetime.now()

#initializing repeat to y to enter the while loop
repeat = 'y'

#repeating the program while unless the user does not want to repeat
while repeat == 'y':
    
    #connecting to MicroLoad
    c = FloatModbusClient(host= ip1, port=502, unit_id = 1, auto_open=True)
    
    #checks to see if MicroLoad connection is open
    if c.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to MicroFlow")
        #collecting date/time for MicroFlow
        Microhour = c.read_input_registers(1670,1)
        Microminute = c.read_input_registers(1669,1)
        Microsecond = c.read_input_registers(1668,1)
        Microday = c.read_input_registers(1666,1)
        Micromonth = c.read_input_registers(1665,1)
        Microyear = c.read_input_registers(1664,1)
        #assigning values as strings to MicroTime and MicroDate ([1:-1] removes bracket from data ouput)
        MicroTime = str(Microhour)[1:-1] + str(":") + str(Microminute)[1:-1] + str(":") + str(Microsecond)[1:-1]
        MicroDate = str(Microday)[1:-1] + str("/") + str(Micromonth)[1:-1] + str("/") + str(Microyear)[1:-1]
        # collecting float values from MicroFlow using modbus adresses
        MicroCTL = c.read_float(4,4874,1)[0]
        MicroCPL = c.read_float(4,4876,1)[0]
        MicroCTPL = c.read_float(4,4888,1)[0]
        MicroRefTemp = c.read_float(4,6916, 1)[0]
        MicroMainTemp = c.read_float(3,25380,1)[0]
        MicroAvgTemp = c.read_float(4,2818,1)[0]
        MicroLiveTemp = c.read_float(4,6920,1 )[0]
        MicroMainPres = c.read_float(3,25392,1)[0] 
        MicroAvgPres = c.read_float(4,2822,1)[0]
        MicroLivePres = c.read_float(3,6924,1)[0]
        MicroRefDens = c.read_float(3,25386,1)[0]
        MicroAvgDens = c.read_float(4,2820,1)[0]
        MicroLiveDens = c.read_float(3,6922,1)[0]
        #collecting double data from MicroFlow using modbus addresses
        MicroIV = c.read_double(4, 3072, 1)[0]
        MicroGV = c.read_double(4, 3076, 1)[0]
        MicroGST = c.read_double(4, 3080, 1)[0]
        MicroGSV = c.read_double(4, 3084, 1)[0]
        Micrometerfactor = c.read_double(4, 2816, 1)[0]
        MicroBSW = c.read_double(4, 2838, 1)[0]
        Micromass = c.read_double(4, 3088, 1)[0]
        Micropulse = c.read_double(4, 5120, 1)[0]
        #setting values to N/A because they are not available in the MicroLoad
        MicroNSV = "N/A"
        MicroKfactor = "N/A"
        #closing the connection to the MicroFlow
        c.close()
    else:
        #letting the user know that the device isn't connected
        print("MicroFlow not connected")
        #assigning all values to N/A because MicroLoad isn't connected
        Microhour = "N/A"
        Microminute = "N/A"
        Microsecond = "N/A"
        Microday = "N/A"
        Micromonth = "N/A"
        Microyear = "N/A"
        MicroTime = "N/A"
        MicroDate = "N/A"
        MicroCTL = "N/A"
        MicroCPL = "N/A"
        MicroCTPL = "N/A"
        MicroRefTemp = "N/A"
        MicroMainTemp = "N/A"
        MicroAvgTemp = "N/A"
        MicroLiveTemp = "N/A"
        MicroMainPres = "N/A"
        MicroAvgPres = "N/A"
        MicroLivePres = "N/A"
        MicroRefDens = "N/A"
        MicroAvgDens = "N/A"
        MicroLiveDens = "N/A"
        MicroIV = "N/A"
        MicroGV = "N/A"
        MicroGST = "N/A"
        MicroGSV = "N/A"
        MicroNSV = "N/A"
        MicroKfactor = "N/A"
        Micrometerfactor = "N/A"
        MicroBSW = "N/A"
        Micromass = "N/A"
        Micropulse = "N/A"

    #connecting to AccuLoad
    d = FloatModbusClient(host= ip2, port=502, unit_id = 1, auto_open=True)

    #checks to see if connection to AccuLoad is open
    if d.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to AccuLoad")
        #collecting date/time for AccuLoad
        ALhour = d.read_input_registers(2502,1)
        ALminute = d.read_input_registers(2501,1)
        ALsecond = d.read_input_registers(2500,1)
        ALday = d.read_input_registers(2498,1)
        ALmonth = d.read_input_registers(2497,1)
        ALyear = d.read_input_registers(2496,1)
        #assigning values as strings to ALTime and ALDate ([1:-1] removes bracket from data ouput)
        ALTime = str(ALhour)[1:-1] + str(":") + str(ALminute)[1:-1] + str(":") + str(ALsecond)[1:-1]
        ALDate = str(ALday)[1:-1] + str("/") + str(ALmonth)[1:-1] + str("/") + str(ALyear)[1:-1]
        #collecting float values from AccuLoad using modbus adresses
        AccuCTL = d.read_float(4,8124,1)[0]
        AccuCPL = d.read_float(4,8136,1)[0]
        AccuCTPL = d.read_float(4,8208,1)[0]
        AccuRefTemp = d.read_float(3,4048,1)[0]
        AccuMainTemp = d.read_float(3,7082,1)[0]
        AccuLiveTemp = d.read_float(4,6472,1)[0]
        AccuAvgTemp= d.read_float(4,8088,1)[0]
        AccuMainPres = d.read_float(3,7094,1)[0]
        AccuAvgPres = d.read_float(4,4358,1)[0]
        AccuLivePres = d.read_float(4,6476,1)[0]
        AccuRefDens = d.read_float(3,7088,1)[0]
        AccuAvgDens = d.read_float(4,4356,1)[0]
        AccuLiveDens = d.read_float(4,6474,1)[0]
        AccuKfactor = d.read_float(3, 5698, 1)[0]
        Accumeterfactor = d.read_float(3, 7058, 1)[0]
        #collecting double data from AccuLoad using modbus addresses
        AccuIV = d.read_double(4, 4480, 1)[0]
        AccuGV = d.read_double(4, 4484, 1)[0]
        AccuGST = d.read_double(4, 4488, 1)[0]
        AccuGSV = d.read_double(4, 4492, 1)[0]     
        Accumass = d.read_double(4, 5712, 1)[0]
        Accupulse = d.read_double(4, 8384, 1)[0]
        #setting values to N/A because they are not available in the ALIV
        AccuBSW = "N/A"
        AccuNSV = "N/A"
        #closing the connection to the AccuLoad
        d.close()
    else:
        #letting the user know that the device isn't connected
        print("AccuLoad not connected")
        #assigning all values to N/A because ALIV isn't connected
        ALhour = "N/A"
        ALminute = "N/A"
        ALsecond = "N/A"
        ALday = "N/A"
        ALmonth = "N/A"
        ALyear = "N/A"
        ALTime = "N/A"
        ALDate = "N/A"
        AccuCTL = "N/A"
        AccuCPL = "N/A"
        AccuCTPL = "N/A"
        AccuRefTemp = "N/A"
        AccuMainTemp = "N/A"
        AccuLiveTemp = "N/A"
        AccuAvgTemp= "N/A"
        AccuMainPres = "N/A"
        AccuAvgPres = "N/A"
        AccuLivePres = "N/A"
        AccuRefDens = "N/A"
        AccuAvgDens = "N/A"
        AccuLiveDens = "N/A"
        AccuIV = "N/A"
        AccuGV = "N/A"
        AccuGST = "N/A"
        AccuGSV = "N/A"
        AccuNSV = "N/A"
        AccuKfactor = "N/A"
        Accumeterfactor = "N/A"
        AccuBSW = "N/A"
        Accumass = "N/A"
        Accupulse = "N/A"

    #connecting to ucos windows
    e = FloatModbusClient(host= ip3, port=502, unit_id = 1, auto_open=True)

    #checks to see if ucos windows connection is open
    if e.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to Windows UCOS")
        #assigning values as strings to windTime and windDate
        windTime = currentDT.strftime("%H:%M:%S")
        windDate = currentDT.strftime("%d/%m/%Y")
        #collecting float values from ucos using modbus adresses
        windCTL = e.read_double(3, 1028, 1)[0]
        windCPL = e.read_double(3, 1032, 1)[0]
        windCTPL = e.read_double(3, 1036, 1)[0]
        windLiveTemp = e.read_double(3, 100, 1)[0]
        windLivePres = e.read_double(3, 104 , 1)[0]
        windLiveDens = e.read_double(3, 108, 1)[0]
        #collecting double data from ucos using modbus addresses (still need modbus addresses!!!!)
        windIV = e.read_double(3, 1000, 1)[0]
        windGV = e.read_double(3, 1004, 1)[0]
        windGST = e.read_double(3, 1008, 1)[0]
        windGSV = e.read_double(3, 1012, 1)[0]
        windNSV = e.read_double(3, 1016, 1)[0]
        windBSW = e.read_double(3, 120, 1)[0]
        windkfactor = e.read_double(3, 112, 1)[0]
        windmeterfactor = e.read_double(3, 116, 1)[0]
        windmass = e.read_double(3, 1020, 1)[0]
        windpulse = e.read_double(3, 1024, 1)[0]
        windNSV = e.read_double(3, 1016, 1)[0]
        #setting values to N/A because they are not available in the windows UCOS 
        windRefDens = "N/A"
        windAvgDens = "N/A"
        windAvgTemp= "N/A"
        windMainPres = "N/A"
        windAvgPres = "N/A"
        windRefTemp = "N/A"
        windMainTemp = "N/A"
        #closing the connection to the windows ucos
        e.close()
    else:
        #letting the user know that the device isn't connected
        print("Windows UCOS not connected")
        #assigning all values to N/A because ucos isn't connected
        windhour = "N/A"
        windminute = "N/A"
        windsecond = "N/A"
        windday = "N/A"
        windmonth = "N/A"
        windyear = "N/A"
        windTime = "N/A"
        windDate = "N/A"
        windCTL = "N/A"
        windCPL = "N/A"
        windCTPL = "N/A"
        windRefTemp = "N/A"
        windMainTemp = "N/A"
        windLiveTemp = "N/A"
        windAvgTemp= "N/A"
        windMainPres = "N/A"
        windAvgPres = "N/A"
        windLivePres = "N/A"
        windRefDens = "N/A"
        windAvgDens = "N/A"
        windLiveDens = "N/A"
        windIV = "N/A"
        windGV = "N/A"
        windGST = "N/A"
        windGSV = "N/A"
        windNSV = "N/A"
        windBSW = "N/A"
        windkfactor = "N/A"
        windmeterfactor = "N/A"
        windmass = "N/A"
        windpulse = "N/A"
        
    #connecting to linux ucos    
    h = FloatModbusClient(host= ip3, port=502, unit_id = 2, auto_open=True)
        
#checks to see if ucos linux connection is open
    if h.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to Linux UCOS")
        #assigning values as strings to linTime and linDate
        linTime = currentDT.strftime("%H:%M:%S")
        linDate = currentDT.strftime("%d/%m/%Y")
        #collecting float values from ucos linux using modbus adresses
        linCTL = h.read_double(3, 1028, 1)[0]
        linCPL = h.read_double(3, 1032, 1)[0]
        linCTPL = h.read_double(3, 1036, 1)[0]
        linLiveTemp = h.read_double(3, 100, 1)[0]
        linLivePres = h.read_double(3, 104 , 1)[0]
        linLiveDens = h.read_double(3, 108, 1)[0]
        #collecting double data from ucos linux using modbus addresses (still need modbus addresses!!!!)
        linIV = h.read_double(3, 1000, 1)[0]
        linGV = h.read_double(3, 1004, 1)[0]
        linGST = h.read_double(3, 1008, 1)[0]
        linGSV = h.read_double(3, 1012, 1)[0]
        linNSV = h.read_double(3, 1016, 1)[0]
        linBSW = h.read_double(3, 120, 1)[0]
        linkfactor = h.read_double(3, 112, 1)[0]
        linmeterfactor = h.read_double(3, 116, 1)[0]
        linmass = h.read_double(3, 1020, 1)[0]
        linpulse = h.read_double(3, 1024, 1)[0]
        linNSV = h.read_double(3, 1016, 1)[0]
        #setting values to N/A because they are not available in the Linux Ucos 
        linRefDens = "N/A"
        linAvgDens = "N/A"
        linAvgTemp= "N/A"
        linMainPres = "N/A"
        linAvgPres = "N/A"
        linRefTemp = "N/A"
        linMainTemp = "N/A"
        #closing the connection to the ucos linux
        h.close()
    else:
        #letting the user know that the device isn't connected
        print("Linux UCOS not connected")
        #assigning all values to N/A because ucos isn't connected
        linhour = "N/A"
        linminute = "N/A"
        linsecond = "N/A"
        linday = "N/A"
        linmonth = "N/A"
        linyear = "N/A"
        linTime = "N/A"
        linDate = "N/A"
        linCTL = "N/A"
        linCPL = "N/A"
        linCTPL = "N/A"
        linRefTemp = "N/A"
        linMainTemp = "N/A"
        linLiveTemp = "N/A"
        linAvgTemp= "N/A"
        linMainPres = "N/A"
        linAvgPres = "N/A"
        linLivePres = "N/A"
        linRefDens = "N/A"
        linAvgDens = "N/A"
        linLiveDens = "N/A"
        linIV = "N/A"
        linGV = "N/A"
        linGST = "N/A"
        linGSV = "N/A"
        linNSV = "N/A"
        linBSW = "N/A"
        linkfactor = "N/A"
        linmeterfactor = "N/A"
        linmass = "N/A"
        linpulse = "N/A"
        
        
        
    #connecting to Omni
    f = FloatModbusClient(host= ip4, port=502, unit_id = 1, auto_open=True)

    #checks to see if omni conncecion is open
    if f.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to Omni")
        #collecting date/time for OMNI
        OMNIhour = f.read_input_registers(3867,1)
        OMNIminute = f.read_input_registers(3868,1)
        OMNIsecond = f.read_input_registers(3869,1)
        OMNIday = f.read_input_registers(3871,1)
        OMNImonth = f.read_input_registers(3870,1)
        OMNIyear = f.read_input_registers(3872,1)
        #assigning values as strings to ALTime and ALDate ([1:-1] removes bracket from data ouput)
        OMNITime = str(OMNIhour)[1:-1] + str(":") + str(OMNIminute)[1:-1] + str(":") + str(OMNIsecond)[1:-1]
        OMNIDate = str(OMNIday)[1:-1] + str("/") + str(OMNImonth)[1:-1] + str("/") + str(OMNIyear)[1:-1]
        #collecting float values from Omni using modbus adresses
        #print(OMNICTL)
        OMNICPL = f.read_float(3,7128,1)[0]
        OMNICTPL = f.read_float(3,8528,1)[0]
        OMNIRefTemp = f.read_holding_registers(7150,1)[0]
        OMNILiveTemp = f.read_float(3,7105,1)[0]        
        OMNIAvgTemp= f.read_float(3,7118,1)[0]
        OMNIAvgPres = f.read_float(3,7119,1)[0]        
        OMNILivePres = f.read_float(3,7106,1)[0]
        OMNIAvgDens = f.read_float(3,7120,1)[0]
        OMNILiveDens = f.read_float(3,7109,1)[0]        
        OmniGV1 = str(f.read_long(3,5101,1)[0])[1:-1]
            #adding the implied decimal
        OmniGV = OmniGV1[:5] + str(".") + OmniGV1[5:]
        OmniNSV1 = str(f.read_long(3,5102,1)[0])[1:-1]
            #adding the implied decimal
        OmniNSV = OmniNSV1[:5] + str(".") + OmniNSV1[5:]
        OMNIKfactor = f.read_float(3,7140,1)[0]
        OMNImeterfactor1 = str(f.read_long(3,5113,1))[2:-2]
            #adding the implied decimal
        OMNImeterfactor = OMNImeterfactor1[:1] + str(".") + OMNImeterfactor1[1:]
        OMNIMainTemp = f.read_float(3,7165,1)[0]
        OMNImass1 = str(f.read_long(3,5103,1))[2:-2]
            #adding the implied decimal
        OMNImass = OMNImass1[:4] + str(".") + OMNImass1[4:]
        #setting values to N/A because they are not available in the Omni
        OMNIpulse = "N/A"
        OMNIBSW = "N/A"
        OMNIMainPres = "N/A"
        OMNIRefDens = "N/A"
        OmniIV = "N/A"
        OmniGST = "N/A"
        OmniGSV = "N/A"
        OMNICTL = "N/A"        
        #closing the connection to the Omni
        f.close()
    else:
        #letting the user know that the device isn't connected
        print("Omni not connected")
        #assigning all values to N/A because Omni isn't connected
        OMNIhour = "N/A"
        OMNIminute = "N/A"
        OMNIsecond = "N/A"
        OMNIday = "N/A"
        OMNImonth = "N/A"
        OMNIyear = "N/A"
        OMNITime = "N/A"
        OMNIDate = "N/A"
        OMNICTL = "N/A"
        OMNICPL = "N/A"
        OMNICTPL = "N/A"
        OMNIRefTemp = "N/A"
        OMNILiveTemp = "N/A"
        OMNIMainTemp = "N/A"
        OMNIAvgTemp= "N/A"
        OMNIMainPres = "N/A"
        OMNIAvgPres = "N/A" 
        OMNILivePres = "N/A"
        OMNIAvgDens = "N/A"
        OMNILiveDens = "N/A"
        OMNIRefDens = "N/A"
        OmniIV = "N/A"
        OmniGV = "N/A"
        OmniGST = "N/A"
        OmniGSV = "N/A"
        OmniNSV = "N/A"
        OMNIKfactor = "N/A"
        OMNImeterfactor = "N/A"
        OMNIBSW = "N/A"
        OMNImass = "N/A"
        OMNIpulse = "N/A"

    #connecting to Spirit
    g = FloatModbusClient(host= ip5, port=502, unit_id = 1, auto_open=True)

    if g.open():
        #letting the user know that the device is connected and data is being read
        print("Connected to Spirit")
        #collecting date/time for Spirit
        #Spirithour = g.read_holding_registers(250,1)
        #Spiritminute = g.read_holding_registers(251,1)
        #Spiritsecond = g.read_holding_registers(252,1)
        #Spiritday = g.read_holding_registers(254,1)
        #Spiritmonth = g.read_holding_registers(253,1)
        #Spirityear = g.read_holding_registers(255,1)
        #assigning values as strings to SpiritTime and SpiritDate ([1:-1] removes bracket from data ouput)
        #SpiritTime = str(Spirithour)[1:-1] + str(":") + str(Spiritminute)[1:-1] + str(":") + str(Spiritsecond)[1:-1]
        #SpiritDate = str(Spiritday)[1:-1] + str("/") + str(Spiritmonth)[1:-1] + str("/") + str(Spirityear)[1:-1]
        SpiritTime = currentDT.strftime("%H:%M:%S") 
        SpiritDate = currentDT.strftime("%d/%m/%Y") 
        #collecting float values from Spirit using modbus adresses
        SpiritCTL = g.read_float(3,2644,1)[0]
        SpiritCPL = g.read_float(3,2645,1)[0]       
        SpiritCTPL = g.read_float(3,2646,1)[0]
        SpiritLiveTemp = g.read_float(3,3580,1)[0]
        SpiritAvgTemp= g.read_float(3,3400,1)[0]
        SpiritAvgPres = g.read_float(3,3401,1)[0]
        SpiritLivePres = g.read_float(3,2601,1)[0]
        SpiritAvgDens = g.read_float(3,3405,1)[0]
        SpiritLiveDens = g.read_float(3,2643,1)[0]
        SpiritBSW = g.read_float(3,2610,1)[0]
        #collecting double data from Spirit using modbus addresses (still need modbus addresses!!!!)
        SpiritIV = g.read_double(3,2820,1)[0]
        SpiritGV = g.read_double(3,2821,1)[0]
        SpiritGSV = g.read_double(3,2822,1)[0]
        SpiritNSV = g.read_double(3,2823,1)[0]
        SpiritKfactor = g.read_float(3,3418,1)[0]
        Spiritmeterfactor = g.read_float(3,3419,1)[0]  
        Spiritmass = g.read_double(3,2824,1)[0]
        Spiritpulse = g.read_double(3,2805,1)[0]
        #setting values to N/A because they are not available in the spirit
        SpiritRefDens = "N/A"
        SpiritMainPres = "N/A"
        SpiritRefTemp = "N/A"
        SpiritMainTemp = "N/A"
        SpiritGST = "N/A"
        
        
        #closing the connection to the Spirit
        g.close()
    else:
        #letting the user know that the device isn't connected
        print("Spirit not connected")
        #assigning all values to N/A because the spirit isn't connected
        Spirithour = "N/A"
        Spiritminute = "N/A"
        Spiritsecond = "N/A"
        Spiritday = "N/A"
        Spiritmonth = "N/A"
        Spirityear = "N/A"
        SpiritTime = "N/A"
        SpiritDate = "N/A"
        SpiritCTL = "N/A"
        SpiritCPL = "N/A"
        SpiritCTPL = "N/A"
        SpiritRefTemp = "N/A"
        SpiritMainTemp = "N/A"
        SpiritLiveTemp = "N/A"
        SpiritAvgTemp= "N/A"
        SpiritMainPres = "N/A"
        SpiritAvgPres = "N/A"
        SpiritLivePres = "N/A"
        SpiritRefDens = "N/A"
        SpiritAvgDens = "N/A"
        SpiritLiveDens = "N/A"
        SpiritIV = "N/A"
        SpiritGV = "N/A"
        SpiritGST = "N/A"
        SpiritGSV = "N/A"
        SpiritNSV = "N/A"
        SpiritKfactor = "N/A"
        Spiritmeterfactor = "N/A"
        SpiritBSW = "N/A"
        Spiritmass = "N/A"
        Spiritpulse = "N/A"
        
        
    #opening and naming the csv file so it can be written to
    with open('LACT_data.csv','a') as LACT_data:
        LACT_data_writer = csv.writer(LACT_data)
        #giving each of the columns a heading
        LACT_data_writer.writerow(['   ', 'MicroFlow', 'AccuLoad', 'UCOS Windows', 'UCOS Linux','Omni', 'Spirit'])
        #adding the date from each device to each column
        LACT_data_writer.writerow(['Date', MicroDate, ALDate, windDate, linDate, OMNIDate, SpiritDate])
        #adding the time from each device to each column
        LACT_data_writer.writerow(['Time', MicroTime, ALTime, windTime, linTime, OMNITime, SpiritTime])
        #assigning IV values to each column 
        LACT_data_writer.writerow(['IV', MicroIV, AccuIV, windIV, linIV, OmniIV, SpiritIV])
        #assigning GV values to each column
        LACT_data_writer.writerow(['GV', MicroGV, AccuGV, windGV, linGV, OmniGV, SpiritGV])
        #assigning GST values to each column
        LACT_data_writer.writerow(['GST', MicroGST, AccuGST, windGST, linGST, OmniGST, SpiritGST])
        #assigning GSV values to each column
        LACT_data_writer.writerow(['GSV', MicroGSV, AccuGSV, windGSV, linGSV, OmniGSV, SpiritGSV])
        #assigning NSV values to each column
        LACT_data_writer.writerow(['NSV', MicroNSV, AccuNSV, windNSV, linNSV, OmniNSV, SpiritNSV])
        #assigning CTL values to each column
        LACT_data_writer.writerow(['CTL', MicroCTL, AccuCTL, windCTL, linCTL, OMNICTL, SpiritCTL])
        #assigning CPL values to each column
        LACT_data_writer.writerow(['CPL', MicroCPL, AccuCPL, windCPL, linCPL, OMNICPL, SpiritCPL])
        #assigning CTPL values to each column
        LACT_data_writer.writerow(['CTPL', MicroCTPL, AccuCTPL, windCTPL, linCTPL, OMNICTPL, SpiritCTPL])
        #assigning ref temp to each column
        LACT_data_writer.writerow(['Ref. Temp.', MicroRefTemp, AccuRefTemp, windRefTemp, linRefTemp, OMNIRefTemp, SpiritRefTemp])
        #assigning maintainence temp to each column
        LACT_data_writer.writerow(['Main. Temp.', MicroMainTemp, AccuMainTemp, windMainTemp, linMainTemp, OMNIMainTemp, SpiritMainTemp])
        #assigning Live temp to each column
        LACT_data_writer.writerow(['Live Temp.', MicroLiveTemp, AccuLiveTemp, windLiveTemp, linLiveTemp, OMNILiveTemp, SpiritLiveTemp])
        #assigning average temp to each column
        LACT_data_writer.writerow(['Avg. Temp.', MicroAvgTemp, AccuAvgTemp, windAvgTemp, linAvgTemp, OMNIAvgTemp, SpiritAvgTemp])
        #assigning maintainence pressure to each column
        LACT_data_writer.writerow(['Main. Pressure', MicroMainPres, AccuMainPres, windMainPres, linMainPres, OMNIMainPres, SpiritMainPres])
        #assigning average pressure to each column
        LACT_data_writer.writerow(['Avg. Pressure', MicroAvgPres, AccuAvgPres, windAvgPres, linAvgPres, OMNIAvgPres, SpiritAvgPres])
        #assigning live pressure to each column
        LACT_data_writer.writerow(['Live Pressure', MicroLivePres, AccuLivePres, windLivePres, linLivePres, OMNILivePres, SpiritLivePres])
        #assigning reference density to each column
        LACT_data_writer.writerow(['Ref. Density', MicroRefDens, AccuRefDens, windRefDens, linRefDens, OMNIRefDens, SpiritRefDens])
        #assigning average density to each column
        LACT_data_writer.writerow(['Avg. Density', MicroAvgDens, AccuAvgDens, windAvgDens, linAvgDens, OMNIAvgDens, SpiritAvgDens])
        #assigning live density to each column
        LACT_data_writer.writerow(['Live Density', MicroLiveDens, AccuLiveDens, windLiveDens, linLiveDens, OMNILiveDens, SpiritLiveDens])
        #assigning k factor to each column
        LACT_data_writer.writerow(['K Factor', MicroKfactor, AccuKfactor, windkfactor, linkfactor, OMNIKfactor, SpiritKfactor])
        #assigning meter factor to each column
        LACT_data_writer.writerow(['Meter Factor', Micrometerfactor, Accumeterfactor, windmeterfactor, linmeterfactor, OMNImeterfactor, Spiritmeterfactor])
        #assigning bs&w
        LACT_data_writer.writerow(['BS&W', MicroBSW, AccuBSW, windBSW, linBSW, OMNIBSW, SpiritBSW])
        #assigning mass to each column
        LACT_data_writer.writerow(['Mass', Micromass, Accumass, windmass, linmass, OMNImass, Spiritmass])
        #assigning pulse total to each column
        LACT_data_writer.writerow(['Pulse Total', Micropulse, Accupulse, windpulse, linpulse, OMNIpulse, Spiritpulse])
        #adding space between runs
        LACT_data_writer.writerow(['        ', '        ', '        ', '        ', '        ', '        '])
        #adding space between runs
        LACT_data_writer.writerow(['        ', '        ', '        ', '        ', '        ', '        '])
        #adding space between runs
        LACT_data_writer.writerow(['        ', '        ', '        ', '        ', '        ', '        '])
    #closing the csv file     
    LACT_data.close()
    
    #asking the user if they would like to run the program again
    repeat = input("Would you like to collect data again? (y/n): ")
    
    #will enter this if statement if the user would like to repeat this program
    if repeat == 'y':
        #asking the user if they would like to use the same ips
        ip_repeat = input("Would you like to use the same ip adresses? (y/n): ")
        #will enter this if statement if the user would like to enter new ips
        if ip_repeat == 'n':
            #prompting the user to enter the ip for each device
            ip1 = input("Enter MicroFlow ip address (Press enter if MicroFlow is unused): ")
            ip2 = input("Enter AccuLoad ip address (Press enter if AccuLoad is unused): ")
            ip3 = input("Enter UCOS ip address (Press enter if UCOS is unused): ")
            ip4 = input("Enter Omni ip address (Press enter if Omni is unused): ")
            ip5 = input("Enter Spirit ip address (Press enter if Spirit is unused): ")