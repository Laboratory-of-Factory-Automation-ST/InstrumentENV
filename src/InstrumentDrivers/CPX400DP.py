# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:26:50 2024

@author: marek novotny
"""
import time

class CPX400DP:
    def __init__(self, con_str, resources, verbose=False):
        self.__con_str = con_str
        self.__resources = resources
        self.__connection = self.__resources.open_resource(self.__con_str)
        self.__verbose = verbose

    def connect(self):
        self.__connection = self.__resources.open_resource(self.__con_str)

    def disconnect(self):
        self.__connection.write("LOCAL")
        self.__connection.close()

    def get_voltage(self, channel):
        return self.__connection.query("V" + str(channel) + "?", 1e-3)

    def set_voltage(self, channel, value):
        self.__connection.write("V" + str(channel) + " " + str(value))

    def get_current(self, channel):
        return self.__connection.query("I" + str(channel) + "?", 1e-3)

    def set_current(self, channel, value):
        self.__connection.write("I" + str(channel) + " " + str(value))

    def out_on(self, channel):
        self.__read_lim_status_reg_raw(channel)
        self.__connection.write("OP" + str(channel) + " 1")
        if self.__verbose:
            print("-> Switching OUT" + str(channel) + " on")
            #self.report_lim_status(channel)

    def out_off(self, channel):
        self.__connection.write("OP" + str(channel) + " 0")
        if self.__verbose:
            print("-> Switching OUT" + str(channel) + " off")
            self.report_lim_status(channel)

    def out_status(self, channel):
        return self.__connection.query("OP" + str(channel) + "?", 1e-3)

    def lock(self):
        if self.__connection.query("IFLOCK", 1e-3).strip() == "1":
            return "-> successfuly locked"
        else:
            return "! lock failed refer to instrument manual for possible causes"

    def unlock(self):
        if self.__connection.query("IFUNLOCK", 1e-3).strip() == "0":
            return "-> successfuly unlocked"
        else:
            return "! unlock failed refer to instrument manual for possible causes"

    def __read_lim_status_reg_raw(self, channel):
        return bin(int(self.__connection.query("LSR" + str(channel) + "?")))
    
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
                    print("+ Output entered voltage limit")
                case 1:
                    print("+ Output entered current limit")
                case 2:
                    print("+ Overvoltage protection engaged")
                case 3:
                    print("+ Overcurrent protection engaged")
                case 4:
                    print("+ Output power limitation engaged")
                case 6:
                    print("+ Hard trip occured - perform manual reset")
        print("]")
                