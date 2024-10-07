# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from src.product_scripts import ips8200hq
from src.instrument_drivers.daq import DAQ
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.DMM6500 import DMM6500
from src.instrument_drivers.generic import Config

"""
Usage example:
    ips8200hq.ips8200hq_out16a1_pgood_convex_ramp()
Please keep your custom main code on your private branches
"""

Config.SET_LOGLEVEL = Config.LogLevel.DEBUG

ID = InstrumentDiscovery()
dmm_con, dmm = ID.allocate(DMM6500, interactive = False)
with dmm_con, dmm:
    chan2 = dmm(DMM6500.Mode.DCVMeter, 2)
    with chan2:
        print(chan2.acquire_measurement())

exit()

with DAQ(InstrumentDiscovery()) as meas:
    meas(DAQ.Mode.Power, DAQ.Params((0, 50),(0, 0.01)))
