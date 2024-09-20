# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:26:50 2024

@author: marek novotny
"""
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty
import logging
import time

class CPX400DP(Instrument):
    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("ASRL4::INSTR")
        addresses.add("ASRL11::INSTR")
        
        return addresses

    def __init__(self, connection: InstrumentConnection, mode):
        super().__init__(connection, Instrument.Mode.Default)

    def release(self):
        self._connection.send("LOCAL")

    def stop(self):
        self.out_off(1)
        self.out_off(2)

    def get_voltage(self, channel):
        return self._connection.send_query("V" + str(channel) + "?", 1e-3)

    def set_voltage(self, channel, value):
        self._connection.send("V" + str(channel) + " " + str(value))
        # self.daq_series.add_data_point(self.get_voltage())

    def get_current(self, channel):
        return self._connection.send_query("I" + str(channel) + "?", 1e-3)

    def set_current(self, channel, value):
        self._connection.send("I" + str(channel) + " " + str(value))

    def out_on(self, channel, blanking_time = 1):
        time.sleep(blanking_time)
        self.__read_lim_status_reg_raw(channel)
        self._connection.send("OP" + str(channel) + " 1")
        logging.info("-> Switching OUT" + str(channel) + " on")
        #self.report_lim_status(channel)

    def out_off(self, channel, blanking_time = 1):
        time.sleep(blanking_time)
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

        logging.warning("OUT" + str(channel) + " Limits [")
        for i, bit in enumerate(active_bits):
            match i:
                case 0:
                    logging.warning("+ Output reached set voltage limit")
                case 1:
                    logging.warning("+ Output reached set current limit")
                case 2:
                    logging.warning("+ Overvoltage protection engaged")
                case 3:
                    logging.warning("+ Overcurrent protection engaged")
                case 4:
                    logging.warning("+ Output power limitation engaged")
                case 6:
                    logging.warning("+ Hard trip occured - perform manual reset")
        logging.warning("]")

    def ramp_voltage(self, channel, init_val, final_val, blanking_time = 50e-3):
        ramp_range = range(init_val * 10, final_val * 10 + 1) if init_val < final_val else reversed(range(final_val * 10, init_val * 10 + 1))
        for i in ramp_range:
            time.sleep(blanking_time)
            self.set_voltage(channel, i / 10)
