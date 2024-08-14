# -*- coding: utf-8 -*-
"""
Created on Mon Feb 12 16:15:53 2024

@author: marek novotny
"""

from pyvisa import ResourceManager
from src.InstrumentDrivers.InstrumentConnection import InstrumentConnection
import logging

class InstrumentDiscovery:
    def __init__(self):
        self.__resources = ResourceManager()
        self.__discovered = list(self.__resources.list_resources())
        self.__handshakes = dict()
        self.get_handshakes()

    def __del__(self):
        logging.info("-> Resources successfully released")
        self.__resources.close()

    @property
    def handshakes(self):
        return self.__handshakes

    def get_handshakes(self) -> None:
        for idx, addr in enumerate(self.__discovered):
            with InstrumentConnection(addr, self.__resources) as con:
                try:
                    inst_name = con.send_query("*IDN?", 1e-3)
                    logging.info(f"-> [{ str(idx) }] { addr } { inst_name }\n")
                    self.__handshakes[addr] = inst_name
                except:
                    logging.warning(f"[{ str(idx) }] { addr } DISCOVERED RESOURCE TIMED OUT\n")

    def get_instrument_address(self, idx):
        try:
            return self.__discovered[idx]
        except:
            logging.warning("-> Instrument was not found")
    
    @property
    def connection_handler(self):
        return self.__resources
