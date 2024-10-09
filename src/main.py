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

ID = InstrumentDiscovery()

# allocate generic instruments of given type
dmm_con, dmm = ID.allocate(DMM6500, interactive = False)
with dmm_con, dmm:
    # type cast generic instrument to the correct internal type
    dmm: DMM6500
    # call a channel of the instrument
    chan2 = dmm(2, DMM6500.Mode.DCVMeter)
    chan3 = dmm(3, DMM6500.Mode.R2PoleMeter)
    # make measurement from the channel
    print(chan2.acquire_measurement())
    print(chan3.acquire_measurement())
    # make measurement from the instrument disconnects channels and reverts to last mode
    dmm.acquire_measurement()
