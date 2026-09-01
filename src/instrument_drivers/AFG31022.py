# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:26:50 2024

@author: marek novotny
"""
from enum import StrEnum
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.Instrument import Instrument
from src.instrument_drivers.generic import classproperty
import logging
import time

class AFG31022(Instrument):
    class WaveShape(StrEnum):
        DC = "DC"
        SINE = "SIN"
        SQUARE = "SQU"
        PULSE = "PULS"
        RAMP = "RAMP"

    @classproperty
    def default_addresses(cls):
        addresses = set()
        addresses.add("USB0::0x0699::0x0356::C020187::INSTR")

        return addresses

    def __init__(self, connection: InstrumentConnection):
        super().__init__(connection)

    def release(self):
        self._connection.send("ABORT")

    def stop(self): 
        self.disable_output(1)
        self.disable_output(2)

    def set_wave_shape(self, channel, shape: WaveShape):
        self._connection.send(f"SOUR{channel}:FUNC:SHAP {shape}")

    def set_wave_freq(self, channel, frequency):
        self._connection.send(f"SOUR{channel}:FREQ:FIX {frequency}")

    def set_wave_phase(self, channel, degrees):
        self._connection.send(f"SOUR{channel}:PHAS:ADJ {degrees}DEG")
    
    def set_wave_high_level(self, channel, level):
        self._connection.send(f"SOUR{channel}:VOLT:LEV:IMM:HIGH {level}V")

    def set_wave_low_level(self, channel, level):
        self._connection.send(f"SOUR{channel}:VOLT:LEV:IMM:LOW {level}V")

    def set_wave_offset(self, channel, offset):
        self._connection.send(f"SOUR{channel}:VOLT:LEV:IMM:OFFS {offset}V")

    def enable_output(self, channel):
        self._connection.send(f"OUTP{channel}:STAT ON")

    def disable_output(self, channel):
        self._connection.send(f"OUTP{channel}:STAT OFF")

    def step_dcv(self, channel, init_val, final_val, blanking_time = 50e-3):
        ramp_range = range(init_val * 10, final_val * 10 + 1) if init_val < final_val else reversed(range(final_val * 10, init_val * 10 + 1))
        for i in ramp_range:
            time.sleep(blanking_time)
            self.set_wave_high_level(channel, i / 10)
