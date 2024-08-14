from __future__ import annotations
from datetime import datetime
from pathlib import Path
import csv
import logging

""" 
Basic class for creating series of acquired data
"""
class Series:
    def __init__(self, header_name) -> None:
        self.__header = []
        self.__values = []
        self.__header.append(header_name)
    
    def __iter__(self):
        return (val for val in self.__col(0))
    
    def __len__(self):
        return len(self.__values)
    
    def __add__(self, series: Series):
        len_diff = len(series) - len(self)
        justified_series = self.__values + [[] for _ in range(len_diff) if len_diff > 0]
        self.__values = [row + series.values[pos:pos+1][0] for pos, row in enumerate(justified_series)]
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
    
    def add_data_point(self, value):
        self.__values.append([value])

    def unpacked_series(self):
        vals = [[row[num] for row in self.__values] for num in range(len(self.__header))]
        return dict(zip(self.__header, vals))

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
            self.__writeable_series.extend(series)
