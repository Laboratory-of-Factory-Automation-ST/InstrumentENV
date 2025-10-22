
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
from src.product_scripts import IPS1050LQ


# Scripting space

# ITECH init
rm = visa.ResourceManager()
resources = rm.list_resources()
print(resources)


# Instrument adress list
wRunnerID = "USB0::0x05FF::0x1023::5005N62526::INSTR"
eLoadID = "USB0::0x2EC7::0x8700::800830013806940011::INSTR"
pSupplyID = "ASRL4::INSTR"


wRunner = rm.open_resource(wRunnerID)

# Test connection
eLoad = rm.open_resource(eLoadID)
it87_id = eLoad.query("*IDN?")
print(it87_id)
eLoad.close()

eLoadConnection = InstrumentConnection(eLoadID, rm)
eLoad = IT87_ElectronicLoad(eLoadConnection)



IPS1050LQ.currentLimitationScript()


while True:
    pass

# it87_reply = wRunner.query("SYSTem:COMMunicate:LAN:MACaddress?")
# print(it87_reply)

# it87_reply = wRunner.query("SYSTem:NETWork:MACaddress?")
# print(it87_reply)

# wRunner_reply = wRunner.query("LAN:MACaddress?") #proble
# print(it87_reply)

# connect IT87 'USB0::0x2EC7::0x8700::800830013806940011::INSTR'
# IT87 = rm.open_resource('')
# IT87.encoding = "latin-1" # change encoding of returned data