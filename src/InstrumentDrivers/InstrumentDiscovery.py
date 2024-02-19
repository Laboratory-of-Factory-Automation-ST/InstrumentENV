# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:15:53 2024

@author: marek novotny
"""

import pyvisa


class InstrumentDiscovery:
    def __init__(self):
        self.__resources = pyvisa.ResourceManager()
        self.__discovered = self.__resources.list_resources()

    def __connect(self, con_str):
        connection = self.__resources.open_resource(con_str)
        connection.read_termination = '\n'
        connection.write_termination = '\n'
        connection.baudrate = 9600
        connection.timeout = 1000

        return connection
    
    def close(self):
        self.__resources.close()

    def print_instruments(self, verbose=False) -> None:
        for idx, con_str in enumerate(self.__discovered):
            connection = self.__connect(con_str)
            try:
                print("[" + str(idx) + "]", con_str, connection.query("*IDN?", 1e-3))
                print("\n")
            except:
                if (verbose):
                    print(con_str, "DISCOVERED RESOURCE TIMED OUT")
            connection.close()

    def get_connection(self, idx) -> tuple[str, pyvisa.ResourceManager]:
        return (self.__discovered[idx], self.__resources)
