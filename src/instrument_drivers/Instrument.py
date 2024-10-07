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

    class Channel:
        def __init__(self, instrument: Instrument, chan_mode: Instrument.Mode, chan_ref: Instrument.ChanRef = ""):
            self.__reference = chan_ref
            self.__instrument = instrument
            self.__mode = chan_mode

        def __enter__(self):
            self.mode = self.__mode
            return self
        
        def __exit__(self, except_type, except_val, except_trace):
            pass

        @property
        def mode(self):
            return self.__instrument.mode
        
        @mode.setter
        def mode(self, mode):
            mode_ctrl = f'{self.__instrument.MODE_CTRL_CMD} "{mode}", (@{self.__reference})'
            self.__instrument._connection.send(mode_ctrl)
            self.__instrument.assert_mode(mode)

        def acquire_measurement(self):
            self.__instrument.route_channel(self.__reference)
            return self.__instrument.acquire_measurement()

    @classproperty
    def default_addresses(cls):
        raise NotImplementedError("Instrument subclass must implement 'default_addresses' property getter method")
    
    def __init__(self, connection: InstrumentConnection, mode: str = "default"):
        self.__connection = connection
        self.__mode = mode
        self.__set_enum_defaults(self.Mode)
        self.__set_enum_defaults(self.ChanRef)
    
    def __call__(self, chan_mode: Mode, *chan_refs: ChanRef):
        chan = self.Channel(self, chan_mode, chan_refs[0])
        return chan
    
    def __enter__(self):
        if self.__connection.is_open is False:
            self.__connection.__enter__()
        self.mode = self.__mode

        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        logging.info("-> Remote lock released")
        self.stop()
        self.release()
        self.reset()

    @property
    def _connection(self):
        return self.__connection

    @property
    def mode(self):
        return self._connection.send_query(f'{self.MODE_CTRL_CMD}?', 10e-3)
    
    @mode.setter
    def mode(self, mode: Mode):
        self.__mode = mode

    def __set_enum_defaults(self, base_enum: StrEnum):
        enum_dict = { i.name : i.value for i in base_enum }
        enum_dict["Default"] = "default"
        extended_enum = StrEnum(base_enum.__name__, enum_dict)
        setattr(self, base_enum.__name__, extended_enum)

    def assert_mode(self, mode: Mode):
        assert self.mode == mode, "Mode assertion error"

    def reset(self):
        self.__connection.send('*RST')
