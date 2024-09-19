# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from src.product_scripts import ips8200hq
from src.instrument_drivers.daq import DAQ
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery

"""
Usage example:
    ips8200hq.ips8200hq_out16a1_pgood_convex_ramp()
Please keep your custom main code on your private branches
"""
with DAQ(InstrumentDiscovery()) as meas:
    meas(DAQ.Mode.Power, DAQ.Params())
