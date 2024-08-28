# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 12:45:09 2024

@author: marek novotny
"""
from InstrumentDiscovery import InstrumentDiscovery
from InstrumentConnection import InstrumentConnection
from DAQ import Series
from DAQ import SeriesWriter
from CPX400DP import CPX400DP
from DMM6500 import DMM6500
import time
from Generic import Config
from Generic import Exceptable

Config.SET_LOGLEVEL = Config.LogLevel.INFO

""" Instrument discovery section """
ID = InstrumentDiscovery()
print(ID.handshakes)

# DEFAULT ADDRESS CONNECTION
ID.default_addresses = DMM6500.default_addresses
datalog1 = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
datalog2 = Exceptable(InstrumentConnection(ID.next_default_address, ID.connection_handler))
with datalog1 as con_d1, datalog2 as con_d2,\
    DMM6500(con_d1.evaluate()) as d1, DMM6500(con_d2.evaluate()) as d2:
    pass

# LAB SRC SWEEP
with Exceptable(InstrumentConnection(ID.get_instrument_address(1), ID.connection_handler, True)) as src_con,\
    CPX400DP(src_con.evaluate()) as src:
    src.set_voltage(2, 10)
    src.set_current(2, 0.5)
    time.sleep(5)
    src.out_on(2)
    time.sleep(5)
    src.sweep_voltage(2, 10, 24)
    src.sweep_voltage(2, 24, 10)
    time.sleep(5)

# MULTIMETER TEST
with Exceptable(InstrumentConnection(ID.get_instrument_address(0), ID.connection_handler)) as multi_con, DMM6500(multi_con.evaluate()) as multi, \
    Exceptable(InstrumentConnection(ID.get_instrument_address(2), ID.connection_handler)) as src_con, CPX400DP(src_con.evaluate()) as src, \
    SeriesWriter(r'./src/Measurements/test.csv') as writer:
    MEAS_preambule = Series("MEAS preambule")
    VDC_src_ser = Series("VDC src")
    VDC_ser = Series("VDC")
    multi.set_v_range(100)
    MEAS_preambule.add_data_point("VRange: 100V")
    src.out_on(1)
    time.sleep(1)
    src.sweep_voltage(1, 0, 20)
    writer.write(MEAS_preambule)
    writer.write(VDC_src_ser + VDC_ser)

# CSV GENERATION TEST
with SeriesWriter(r'./src/Measurements/debug.csv') as writer:
    MEAS_preambule = Series("MEAS preambule")
    VDC_src_ser = Series("VDC src")
    VDC_ser = Series("VDC")
    order_ser = Series("Order")
    empty_ser = Series("empty")
    VDC_src_ser.add_data_point(1)
    VDC_src_ser.add_data_point(3)
    VDC_ser.add_data_point(2)
    VDC_ser.add_data_point(4)
    order_ser.add_data_point(1)
    order_ser.add_data_point(2)
    MEAS_preambule.add_header_field("VRange [V]", "100")
    writer.write(MEAS_preambule)
    writer.write(order_ser + empty_ser + VDC_src_ser + VDC_ser)
