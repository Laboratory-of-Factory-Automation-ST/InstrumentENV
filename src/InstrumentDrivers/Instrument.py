from src.InstrumentDrivers.InstrumentConnection import InstrumentConnection
from enum import Enum

class Instrument:

    class InstrumentType(Enum):
        Datalogger = ()
        PowerSupply = ()
        Scope = ()

    Type = InstrumentType

    def __init__(self, connection: InstrumentConnection, inst_type: InstrumentType):
        if connection is None:
            raise ValueError("InstrumentConnection was not passed to base Instrument constructor!")
        self.__connection = connection
        self.__inst_type = inst_type

    @property
    def _connection(self):
        return self.__connection
    
    @property
    def type(self):
        return self.__inst_type

    def __enter__(self):
        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        print("-> Remote lock released")
        self.stop()
        self.release()
