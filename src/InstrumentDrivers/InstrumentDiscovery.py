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
        self.__default_addresses = None

    def __del__(self):
        logging.info("-> Resources successfully released")
        self.__resources.close()

    def __iter__(self):
        return self
    
    @property
    def next_default_address(self):
        address_served = False
        for addr in self.__default_addresses:
            if addr not in self.__handshakes.keys():
                logging.warning(f"-> Instrument at address {addr} did not respond")
                continue
            address_served = True
            return addr
        if address_served is False:
            logging.error(f"-> Could not discover active instrument address")

    @property
    def handshakes(self):
        return self.__handshakes
    
    @property
    def default_addresses(self):
        return self.__default_addresses
    
    @default_addresses.setter
    def default_addresses(self, addresses):
        self.__default_addresses = addresses

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
