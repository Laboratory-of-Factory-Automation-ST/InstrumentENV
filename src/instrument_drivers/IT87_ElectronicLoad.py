# -*- coding: utf-8 -*-
"""
Created on Mon Sep 29 12:26:50 2025

@author: vojtech elias
"""
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty
import logging
import time

class IT87_ElectronicLoad(Instrument):

    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("USB0::0x2EC7::0x8700::800830013806940011::INSTR")
        return addresses

    class Mode(Instrument.Mode):   
        MEASUREMENT  = "MEASure:"
        DCVMeter = "VOLT:DC"
    #     DCAMeter = "VOLT:AC"
    #     R2PoleMeter = "RES"
    #     R4PoleMeter = "FRES"

    class ChanRef(Instrument.ChanRef):
        CH1_TEMP_REF = "1"
        CH2 = "2"
        CH3 = "3"
        CH4 = "4"
        CH5 = "5"
        CH6 = "6"
        CH7 = "7"
        CH8 = "8"

    def __init__(self, connection: InstrumentConnection):
        #super().__init__(connection, Instrument.Mode.Default)
        super().__init__(connection)

    def idn(self):
        return self._connection.handshake()

    def systemLocal(self):
        self._connection.sendCmd("SYSTem:LOCal")

    def systemRemote(self):
        self._connection.sendCmd("SYSTem:REMote")
    
    def sendCmd(self, it87Cmd):
            self.__connection.sendCmd(it87Cmd)

    def getActiveChannel(self):
        return self._connection.sendQuery("CHANnel?")
        
    def setActiveChannel(self, channel_id):
        if ((channel_id >= 1) & (channel_id <= 8)):
            try:
                channelIdStr = "CHANnel " + str(channel_id)
                self._connection.sendCmd(channelIdStr)
            except Exception as e:
                print(e)
        else:
            # Wrong parameter
            print("Invalid IT87 channel ID: " + str(channel_id)) 

    def getSlewPositive(self):
        return self._connection.sendQuery("CURRent:SLEW:POSitive?")

    def getSlewNegative(self):
        return self._connection.sendQuery("CURRent:SLEW:NEGative?")

    # slew rate in range = 0.001 - 2.5 A/us
    def setSlew(self, AmpsPerMicroSec = 0.01):
        self._connection.sendCmd("CURRent:SLEW:POSitive " + str(AmpsPerMicroSec))
    
    def continuousTransient(self, channel_id, ALEVel_Amps, AWIDth_ms, BLEVel_Amps, BWIDth_ms):

        self._connection.sendCmd("CURRent:TRANsient:MODE CONTinuous")
        self._connection.sendCmd("CURRent:TRANsient:ALEVel " + str(ALEVel_Amps))
        self._connection.sendCmd("CURRent:TRANsient:AWIDth " + str(AWIDth_ms) + "mS")
        self._connection.sendCmd("CURRent:TRANsient:BLEVel " + str(BLEVel_Amps))
        self._connection.sendCmd("CURRent:TRANsient:BWIDth " + str(BWIDth_ms) + "mS")
        self._connection.sendCmd("TRANsient ON")
        self._connection.sendCmd("INPut ON")
        self._connection.sendCmd("TRIGger:IMMediate")

