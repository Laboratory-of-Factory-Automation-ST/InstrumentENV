# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from InstrumentDiscovery import InstrumentDiscovery
from InstrumentConnection import InstrumentConnection
from CPX400DP import CPX400DP
import time

""" Instrument discovery section """
ID = InstrumentDiscovery()
ID.print_instruments()

with InstrumentConnection(ID.get_instrument_address(1), ID.get_connection_handler()) as con, CPX400DP(con, True) as supply:
   
    """ Command execution section """
    print(supply.get_voltage(1))
    print(supply.get_voltage(2))
    supply.set_voltage(1, 12.00)
    print(supply.get_voltage(1))

    print(supply.get_current(1))
    print(supply.get_current(2))
    supply.set_current(1, 1.00)

    print(supply.out_status(1))
    print(supply.out_status(2))

    supply.out_on(1)
    time.sleep(1)
    supply.out_on(2)
    time.sleep(1)
    supply.out_off(2)
    time.sleep(1)
    supply.out_off(1)
    time.sleep(1)
    print(supply.lock())
    time.sleep(1)
    print(supply.unlock())
    supply.release()

# v = 0
# while True:
#     supply.write_voltage(1, v)
#     time.sleep(0.5)
#     v += 1
#     v %= 25
