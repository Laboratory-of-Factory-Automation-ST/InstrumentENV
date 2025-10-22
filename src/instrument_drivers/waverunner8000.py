

# SW needed
# IVI Drivers ((TELEDYNE, interface for controlling and communicating)
# VICP Passport ((TELEDYNE, Plug-in passport for NI VISA)
# NI VISA (API for unified interface for GPIB, LXI, USB instruments)
# ActiveDSO (TELEDYNE)

# Remote desktop, Wavestudio (TELEDYNE), XStream (or Automation) browser 



import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt

# USBTMC init
rm = visa.ResourceManager()
resources = rm.list_resources()
print(resources)
MDA = rm.open_resource('USB0::0x05FF::0x1023::5005N62526::INSTR')
MDA.encoding = "latin-1" # change encoding of returned data

# TCPIP/LXI init
# rm = visa.ResourceManager()
# resources = rm.list_resources()
# MDA = rm.open_resource("TCIP:: ")

HorizontalScale = Scope.query("vbs? 'return=app.Acquisition.Horizontal.HorScale'")

Scope.write("vbs 'app.Acquisition.Horizontal.HorScale = 0.000001'")


#session 2

#command templates
Scope.query("vbs? 'app.Acquisition.'")
Scope.write("vbs 'app.Acquisition.'")

#change trigger mode
Scope.write("vbs 'app.Acquisition.   TBD  '")

#change horizontal scale
Scope.query("vbs? 'return=app.Acquisition.Horizontal.HorScale'")
            
#change vertical scale
VerScale = Scope.query("vbs? '.Acquisition.C1.VerScale'")
print(VerScale)

Scope.write("vbs 'app.Acquisition.C1.VerScale'")


#deskew
#app.Acquisition.C1.Deskew

#cursors
XPOS1 = Scope.query("vbs? 'return = app.Acquisition.Cursors.XPos1 = -0.00002'")
Scope.write("vbs 'app.Acquisition.Cursors.XPos1 = -0.00002'")

#diagnostics
# return = app.Utility.Options.
# return = app.Utility.Options.