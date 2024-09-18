# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 12:12:12 2024

@author: vojtech elias
"""

from serial import Serial, SerialException

class ST_device(): 
    """
    Class provides serial communication object to control Nucleo-based lab tools
    """
    def __init__(self, name):
        self.name = name
        self.com_port = None

    def __del__(self) -> None:
        if(self.com_port is not None):
            self.com_port.close()
        pass

    def bytes_to_str(line_bytes):
        return line_bytes.decode('utf-8')

    def remove_line_end(line):
        return str.removesuffix(line, '\n')

    
    def com_port_connect(self):
        try:
            from serial.tools.list_ports import comports
        except ImportError:
            print(ImportError.__name__ + ': COM port list not imported')
            return None
        
        if comports:
            com_ports_list = list(comports())
            for port in com_ports_list:
                
                if(port.manufacturer == 'STMicroelectronics'):
                    # ST device
                    if(self.com_port == None):
                        # open serial  port
                        try:
                            self.com_port = Serial(port=str(port.device), baudrate=115200, timeout=0.1)
                            if(self.com_port.isOpen):
                                # port succesfully opened
                                print('ST device serial port open at ' + port.device)
                            else:
                                # port not opened
                                print('ST device serial port couldn\'t be open at ' + port.device)                            
                        
                        except SerialException as ex:
                            print(SerialException.__name__ + ': Could not open ' + port.device)  

                        # ST device serial port is defined
                    break                    
                else:
                    #not interested in other devices
                    continue
        return self.com_port

    def send_cmd(self, cmd):
        tx_bytes = str.encode(str(cmd))
        
        # serial port write operation
        try:
            self.com_port.write(tx_bytes)
        except SerialException as ex:
            print('Exception: ' + str(ex))
            return

    def send_query(self, query):

        self.send_cmd(query)

        reply = ''
        while True:
            #read line
            try:
                rx_bytes = self.com_port.readline()
            except SerialException as ex:
                print('Exception: ' + str(ex))
                return
            
            if sum(rx_bytes) == 0:
                return reply
            else:
                rx_string = ST_device.bytes_to_str(rx_bytes)
                reply += rx_string
                continue

    def device_prompt(self):
        
        print(self.name + '@' + self.com_port.port + ' device prompt starting (type \'q\' to quit)\n')

        while True:
            cmd = input(self.name + '_prompt>> ')
            if cmd == 'q':
                break

            reply = self.send_query(cmd)
            print(reply)

        print('leaving ' + self.name + '_prompt')

def nucleo_connect():
    try:
        from serial.tools.list_ports import comports
    except ImportError:
        return "Exception: comports not imported"
    if comports:

        print('serial device list:')
        com_ports_list = list(comports())
        
        serial_device_info = ''
        nucleo_serial_handle = None
        for port in com_ports_list:
            serial_device_info += 'device: ' + port.device + '\n'
            serial_device_info += '\t' + port[1] + '\n'
            serial_device_info += '\t' + port[2] + '\n'

            print(serial_device_info)
            serial_device_info = '' 
            
            if(nucleo_serial_handle == None and port.manufacturer == 'STMicroelectronics'):
                # ST-Link device

                try:
                    nucleo_serial_handle = Serial(port=str(port.device), baudrate=115200, timeout=0.1)
                except SerialException:
                    print(SerialException.__name__ + ': Could not open ' + port.device)  

                if(nucleo_serial_handle.isOpen):
                    # port succesfully opened
                    continue
                    #return ips_board_serial_handle
                else:
                    return None
            
            # try:
            #     candidate.open()
            #     report += "\tSuccessfully opened port\n"
            # except SerialException as ex:
            #     report += "\tCouldn't open port ("+ str(ex) +")\n"
            #     continue
            
            # output = bytearray([0x1b, 0x02, 0x05, 1,2,3,4, 0xAA, 0x55])
            # candidate.write(output)
            # candidate.close()

        return nucleo_serial_handle
    else:
        return None

'''scripting space''' 
print('\nscript starting\n')

nucleo = ST_device('nucleo')
if (nucleo.com_port_connect() is not None):
    nucleo.device_prompt()
else:
    print('ST device not connected')

# ips_board_serial_handle = nucleo_connect()
# if ips_board_serial_handle is not None:
#     ips_prompt(ips_board_serial_handle)
# else:
#     print('ST-Link device not detected')
 
print('script ending\n')

'''end of scripting space'''

#TODO check for null return (nucleo not connected, more nucleos connected)
#TODO Exceptions handling when nucleo is disnonnected during runtime
#TODO tbd

