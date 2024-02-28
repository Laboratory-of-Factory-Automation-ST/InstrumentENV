# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:15:53 2024

@author: marek novotny
"""

from pyvisa import ResourceManager
from InstrumentConnection import InstrumentConnection


class InstrumentDiscovery:
    __resources = ResourceManager()

    def __init__(self):
        self.__discovered = self.__resources.list_resources()

    def __del__(self):
        print("-> Resources successfully released")
        self.__resources.close()

    def print_instruments(self, verbose=False) -> None:
        for idx, addr in enumerate(self.__discovered):
            with InstrumentConnection(addr, self.__resources) as con:
                try:
                    print("[" + str(idx) + "]", addr, con.query("*IDN?", 1e-3))
                    print("\n")
                except:
                    if (verbose):
                        print(addr, "DISCOVERED RESOURCE TIMED OUT")

    def get_instrument_address(self, idx):
        return self.__discovered[idx]
    
    def get_connection_handler(self):
        return self.__resources
