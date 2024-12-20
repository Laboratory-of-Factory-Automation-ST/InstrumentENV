from __future__ import annotations
from src.instrument_drivers.InstrumentConnection import InstrumentConnection
from src.instrument_drivers.generic import classproperty
from enum import StrEnum
import logging

class Instrument:
    MODE_CTRL_CMD = ""

    class Mode(StrEnum):
        pass

    class ChanRef(StrEnum):
        pass

    @classproperty
    def default_addresses(cls):
        raise NotImplementedError("Instrument subclass must implement 'default_addresses' property getter method")
    
    def __init__(self, connection: InstrumentConnection, mode: str = "default"):
        self.__connection = connection
        self.__mode = mode
        self.__fallback_mode = None
        self.__channel_reference = None
        self.__set_enum_defaults(self.Mode)
        self.__set_enum_defaults(self.ChanRef)
           
    def __enter__(self):
        if self.__connection.is_open is False:
            self.__connection.__enter__()
        self.mode = self.__mode

        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        logging.info("-> Remote lock released")
        self.stop()
        self.reset()
        self.release()

    @property
    def _connection(self):
        return self.__connection

    @property
    def mode(self):
        return self._connection.send_query(f'{self.MODE_CTRL_CMD}?', 10e-3)
    
    @property
    def fallback_mode(self):
        return self.__fallback_mode
    
    @property
    def channel_reference(self):
        return self.__channel_reference
    
    @mode.setter
    def mode(self, mode: Mode):
        self.__mode = mode

    @fallback_mode.setter
    def fallback_mode(self, mode: Mode):
        self.__fallback_mode = mode

    @channel_reference.setter
    def channel_reference(self, chan_ref):
        self.__channel_reference = chan_ref

    def __set_enum_defaults(self, base_enum: StrEnum):
        enum_dict = { i.name : i.value for i in base_enum }
        enum_dict["Default"] = "default"
        extended_enum = StrEnum(base_enum.__name__, enum_dict)
        setattr(self, base_enum.__name__, extended_enum)

    def assert_mode(self, mode: Mode):
        assert self.mode == mode, "Mode assertion error"

    def reset(self):
        self.__connection.send('*RST')
