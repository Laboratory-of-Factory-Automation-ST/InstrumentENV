# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:26:50 2024

@author: marek novotny
"""
from src.InstrumentDrivers.InstrumentConnection import InstrumentConnection
from src.InstrumentDrivers.Instrument import Instrument
import logging

class CPX400DP(Instrument):
    def __init__(self, connection: InstrumentConnection):
        super().__init__(connection, Instrument.Type.PowerSupply)

    def release(self):
        self._connection.send("LOCAL")

    def stop(self):
        self.out_off(1)
        self.out_off(2)

    def get_voltage(self, channel):
        return self._connection.send_query("V" + str(channel) + "?", 1e-3)

    def set_voltage(self, channel, value):
        # Instrument.DAQ.add_data_column('V_DC src')
        # Instrument.DAQ.add_data_point(value)
        self._connection.send("V" + str(channel) + " " + str(value))

    def get_current(self, channel):
        return self._connection.send_query("I" + str(channel) + "?", 1e-3)

    def set_current(self, channel, value):
        self._connection.send("I" + str(channel) + " " + str(value))

    def out_on(self, channel):
        self.__read_lim_status_reg_raw(channel)
        self._connection.send("OP" + str(channel) + " 1")
        logging.info("-> Switching OUT" + str(channel) + " on")
        #self.report_lim_status(channel)

    def out_off(self, channel):
        self._connection.send("OP" + str(channel) + " 0")
        logging.info("-> Switching OUT" + str(channel) + " off")
        #self.report_lim_status(channel)

    def out_status(self, channel):
        return self._connection.send("OP" + str(channel) + "?", 1e-3)

    def lock(self):
        if self._connection.send_query("IFLOCK", 1e-3).strip() == "1":
            return "-> successfuly locked"
        else:
            return "! lock failed refer to instrument manual for possible causes"

    def unlock(self):
        if self._connection.send_query("IFUNLOCK", 1e-3).strip() == "0":
            return "-> successfuly unlocked"
        else:
            return "! unlock failed refer to instrument manual for possible causes"

    def __read_lim_status_reg_raw(self, channel):
        return bin(int(self._connection.send_query("LSR" + str(channel) + "?", 1e-3)))
    
    def read_lim_status_active_bits(self, channel):
        reg = self.__read_lim_status_reg_raw(channel)
        active_bits = [(len(reg[2:]) - 1 - i) for i, bit in enumerate(reg[2:]) if bit == '1']

        return active_bits

    def report_lim_status(self, channel):
        active_bits = self.read_lim_status_active_bits(channel)

        print("OUT" + str(channel) + " Limits [")
        for i, bit in enumerate(active_bits):
            match i:
                case 0:
                    print("+ Output reached set voltage limit")
                case 1:
                    print("+ Output reached set current limit")
                case 2:
                    print("+ Overvoltage protection engaged")
                case 3:
                    print("+ Overcurrent protection engaged")
                case 4:
                    print("+ Output power limitation engaged")
                case 6:
                    print("+ Hard trip occured - perform manual reset")
        print("]")
                