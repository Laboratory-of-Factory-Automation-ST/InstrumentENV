# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from src.environment import EnvInit
EnvInit()

from src.product_scripts import ips8200hq
from src.instrument_drivers.daq import DAQ
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.DMM6500 import DMM6500
from src.instrument_drivers.AFG31022 import AFG31022
from src.instrument_drivers.CPX400DP import CPX400DP
from src.instrument_drivers.MSO68B import MSO68B
from src.instrument_drivers.generic import Config
from src.instrument_drivers.generic import ContextGuard
from src.instrument_drivers.InstrumentConnection import InstrumentConnection

"""
Usage example:
    ips8200hq.ips8200hq_out16a1_pgood_convex_ramp()
Please keep your custom main code on your private branches
"""
Config.SET_LOGLEVEL = Config.LogLevel.INFO
ID = InstrumentDiscovery()

ID.default_addresses = CPX400DP.default_addresses
src_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))

ID.default_addresses = MSO68B.default_addresses
scope_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))

with src_handle, scope_handle, CPX400DP(src_handle.evaluate()) as src, MSO68B(scope_handle.evaluate()) as scope:
    pass

# gener_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))

# with gener_handle, AFG31022(gener_handle.evaluate()) as gener:
#     gener.set_wave_shape(1, gener.WaveShape.DC)

# ips8200hq.ips8200hq_out16a1_input_concave_ramp(12, 12)
# ips8200hq.ips8200hq_out16a1_input_convex_ramp(12, 12)
