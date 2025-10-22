import pyvisa as visa
from pyvisa import ResourceManager
import numpy as np
import matplotlib.pyplot as plt

import time
from src.instrument_drivers.generic import ContextGuard
from src.instrument_drivers.generic import Config
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.IT87_ElectronicLoad import IT87_ElectronicLoad 
from src.instrument_drivers.CPX400DP import CPX400DP
#from product_scripts import ips1025lq_tests

def currentLimitationScript():
    # Config.SET_LOGLEVEL = log_level
    ID = InstrumentDiscovery()
    
    ID.default_addresses = CPX400DP.default_addresses
    pSupply_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
    
    ID.default_addresses = IT87_ElectronicLoad.default_addresses
    eLoad_handle = ContextGuard(InstrumentConnection(ID.next_default_address, ID.connection_handler))
   
    with \
        pSupply_handle, \
        eLoad_handle, \
        IT87_ElectronicLoad(eLoad_handle.evaluate()) as eLoad, \
        CPX400DP(pSupply_handle.evaluate()) as pSupply\
        :

        print(pSupply._connection.handshake())
        print(eLoad.idn())

        pSupply.set_voltage(2, 3.3)


        pSupply.set_voltage(1, 24)
        pSupply.set_current(1, 10)
        pSupply.out_on(1)
        
        time.sleep(0.1)

        dIdt = eLoad.getSlewPositive()

        dIdt = 0.001
        eLoad.setActiveChannel(1)
        eLoad.setSlew(dIdt)
        eLoad.continuousTransient(1, 0.2, 300, 5, 200)

        while input("Press key") != ('q'):
            eLoad.setSlew(dIdt)
            dIdt = 2*dIdt
            if (dIdt > 0.01):
                dIdt = 0.001
        
        #it87.__connection.sendCmd

        #time.sleep(10)
        #time.sleep(5 if init_hold_time < 5 else init_hold_time)

""" with pSupply_handle, \
        CPX400DP(pSupply_handle.evaluate()) as pSupply: """

""" 
    with eLoad_handle, IT87_ElectronicLoad(eLoad_handle.evaluate()) as eLoad: 
        # CPX400DP(pSupply_handle.evaluate()) as pSupply: """

""" with \
        pSupply_handle, \
        eLoad_handle, \
        IT87_ElectronicLoad(eLoad_handle.evaluate()) as eLoad: 
        CPX400DP(pSupply_handle.evaluate()) as pSupply: """