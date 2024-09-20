from __future__ import annotations
from datetime import datetime
from pathlib import Path
import csv
import logging
from enum import Enum, auto
from src.instrument_drivers.InstrumentDiscovery import InstrumentDiscovery
from src.instrument_drivers.DMM6500 import DMM6500
from src.instrument_drivers.CPX400DP import CPX400DP
import time
import typing

"""
Data acquisition composer class
"""
class DAQ:
    class Mode(Enum):
        Power = auto()

    class Params:
        def __init__(self, voltage_range: tuple[int, int] = (0, 24), current_range: tuple[int, int] = (0, 0.5)):
            self.__v_range = voltage_range
            self.__i_range = current_range

        @property
        def current_range(self):
            return self.__i_range
        
        @property
        def current_limit(self):
            return self.__i_range[1]
        
        @property
        def voltage_range(self):
            return self.__v_range

    def __init__(self, discovery: InstrumentDiscovery):
        self.__discovery = discovery

    def __call__(self, mode: typing.Optional[Mode], params: Params):
        match(mode):
            case self.Mode.Power:
                self.power(params)
            case None:
                pass

    def __enter__(self):
        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        return

    def power(self, params: Params):
        ammeter: DMM6500
        voltmeter_con, voltmeter = self.__discovery.allocate(DMM6500, DMM6500.Mode.DCVMeter)
        voltmeter: DMM6500
        ammeter_con, ammeter = self.__discovery.allocate(DMM6500, DMM6500.Mode.DCAMeter)
        src: CPX400DP
        src_con, src = self.__discovery.allocate(CPX400DP, CPX400DP.Mode.Default, False)

        volts = Series("v")
        amps = Series("i")
        watts = Series("p")
        with voltmeter_con, ammeter_con, src_con, voltmeter, ammeter, src:
            src.set_current(1, params.current_limit)
            src.set_voltage(1, params.voltage_range[0])
            src.out_on(1)
            for v in range(params.voltage_range[0] * 10, params.voltage_range[1] * 10 + 1):
                src.set_voltage(1, v / 10)
                time.sleep(50e-3)
                volt = voltmeter.acquire_measurement()
                amp = ammeter.acquire_measurement()
                volts.add_data_point(volt)
                amps.add_data_point(amp)
                watts.add_data_point(float(volt) * float(amp))
        with SeriesWriter(r"./src/measurements/power.csv") as writer:
            writer.write(volts + amps + watts)
    
""" 
Basic class for creating series of acquired data
"""
class Series:
    def __init__(self, header_name) -> None:
        self.__header = []
        self.__header_fields = []
        self.__values = []
        self.__header.append(header_name)
    
    def __iter__(self):
        return (val for val in self.__values)
    
    def __len__(self):
        return len(self.__values)
    
    def __add__(self, series: Series):
        len_diff_self = len(series) - len(self)
        len_diff_series = len(self) - len(series)
        justified_self = self.__values + [[None] for _ in range(len_diff_self) if len_diff_self > 0]
        justified_series = series.values + [[None] for _ in range(len_diff_series) if len_diff_series > 0]
        self.__values = [row + justified_series[pos:pos+1][0] for pos, row in enumerate(justified_self)]
        self.__header += series.header
        
        return self
    
    def __str__(self):
        return str(self.__values)
    
    def __col(self, num):
        return [row[num] for row in self.__values]
    
    def __row(self, num):
        return self.__values[num]
    
    @property
    def values(self):
        return self.__values
    
    @property
    def header(self):
        return self.__header
    
    @property
    def header_fields(self):
        return self.__header_fields
    
    def add_header_field(self, name, value):
        self.__header_fields.append([name, value])
    
    def add_data_point(self, value):
        self.__values.append([value])

    def unpacked_series(self):
        vals = [[row[num] for row in self.__values] for num in range(len(self.__header))]
        return dict(zip(self.__header, vals))

"""
Class for writing data series to a file in csv format
"""
class SeriesWriter:
        def __init__(self, filename, dry_run = False):
            self.__filename = filename
            self.__dry_run = dry_run
            self.__writeable_series = []
            
        def __enter__(self):
            if self.__dry_run:
                logging.debug("-> Preparing unique file name")
            elif self.__filename is not None:
                file_path = Path(self.__filename)
                self.__filename = file_path.parent.joinpath(file_path.stem + '_' + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + file_path.suffix)
            return self

        def __exit__(self, except_type, except_val, except_trace):
            if self.__dry_run:
                logging.debug("-> Creating data file")
                return
            with self.__filename.resolve().open("w", newline='') as series_file:
                csv_w = csv.writer(series_file, delimiter=";")
                csv_w.writerows(self.__writeable_series)
            logging.info("-> Report file written at " + str(self.__filename))

        def write(self, series: Series):
            self.__writeable_series.append(series.header)
            self.__writeable_series.extend(series.header_fields)
            self.__writeable_series.extend(series)
