#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 14:22:43 2019

@author: pizducha94
"""

import numpy as np
import matplotlib.pyplot as plt
# import io
import os
import pickle
import errno
import time

from collections import deque
# import asyncio


# The range set of the passive probes is given by their gain constant
passive_probes = ['10X', '100X', 'TPP1000']

# Active probes might have their own ranges so a lookup tables are needed
known_probes = {
    'TCP0150': {
        25: np.array([2.5e-3, 5e-3,  1e-2,  2e-2,  5e-2,  1e-1,  2e-1,  5e-1,  1,  2,  5,  10,  20,  50]),
        150: 10 * np.array([2.5e-3, 5e-3,  1e-2,  2e-2,  5e-2,  1e-1,  2e-1,  5e-1,  1,  2,  5,  10,  20,  50])
    }
}


def parseWFMPreamble(response):
    lines = response.split(';')
    preamble = {}
    for line in lines:
        key, value = line.split(' ', 1)
        key = key.replace(':WFMOUTPRE:', '')
        try:
            preamble[key] = float(value)
        except:
            preamble[key] = value.replace('"', '')
            
    return preamble


def parsePreamble(response):
    preamble = response.split(';')
    settings = {}
    for line in preamble:
        key, value = line.split(' ', 1)
        if key[0] == ':':
            key = key[key.rfind(':'):]
        try:
            settings[key] = float(value)
        except:
            settings[key] = value.replace('"', '')
            
    return settings


class Probe:
# =============================================================================
#     def __init__(self,  fields):
#         self.gain = float(fields[0])        # 'PROBE:GAIN'
# 
#         self.resistance = float(fields[1])  # 'RESISTANCE'
#         if self.resistance < 0:
#             self.resistance = None
# 
#         self.units = fields[2]              # 'UNITS'
#         self.id = fields[3]                 # 'ID:TYPE'
#         self.sernum = fields[4]             # 'SERNUMBER'
#         
# =============================================================================
        
    def __init__(self,  fields):
        self.gain = fields['GAIN']    # 'PROBE:GAIN'

        self.resistance = fields['RESISTANCE']  # 'RESISTANCE'
        if self.resistance < 0:
            self.resistance = None

        self.units = fields['UNITS']        # 'UNITS'
        self.id = fields['ID:TYPE']         # 'ID:TYPE'
        self.sernum = fields['SERNUMBER']   # 'SERNUMBER'


    def __str__(self):
        string = 'Gain:          ' + str(self.gain) + '\n' \
                 'Resistance:    ' + str(self.resistance) + '\n' \
                 'Units:         ' + str(self.units) + '\n' \
                 'id:            ' + str(self.id) + '\n' \
                 'Serial Number: ' + str(self.sernum) + '\n'
        return string


class Waveform:
# =============================================================================
#     def __init__(self,  wfm_pre,  ch_pre,  data):
#         self.data = data
# 
#         # Extract the waveform parameters from the waveform preamble
#         self.dt = float(wfm_pre[9])     # 'XINCR'
#         self.tp = int(wfm_pre[11])      # 'PT_OFF'
#         self.ys = float(wfm_pre[13])    # 'YMULT'
#         self.yo = float(wfm_pre[14])    # 'YOFF' -> 'YZERO'
#         self.yz = float(wfm_pre[15])    # 'YZERO' -> '' does not exist anymore.
#         self.np = int(wfm_pre[6])       # 'NR_PT'
# 
#         # Extract parameters from the channel preamble
#         self.vs = float(ch_pre[6])      # 'SCALE' - [unit] / div
#         self.vo = float(ch_pre[3])      # 'OFFSET' - [unit]
#         self.vp = float(ch_pre[5])      # 'POSITION' - [div]
#         self.hs = self.dt * self.np / 10.0
#         self.vu = ch_pre[11]            # 'UNITS' - [unit]
# =============================================================================

    def __init__(self, wfm, vert, data):
        self.data = data
        self.wfm = wfm
        self.vert = vert
        # self.storeParams(wfm_pre, vertical)
        
    # @classmethod
    # def fromWaveform(self, waveform):
    #     self.data = waveform.data

    def storeParams(self, wfm_pre, vertical):
        # Extract the waveform parameters from the waveform preamble
        self.dt = wfm_pre['XINCR']      # 'XINCR'
        self.tp = wfm_pre['PT_OFF']     # 'PT_OFF'
        self.ys = wfm_pre['YMULT']      # 'YMULT'
        self.yo = wfm_pre['YOFF']      # 'YOFF'
        self.yz = wfm_pre['YZERO']   # 'YZERO'
        self.np = wfm_pre['NR_PT']      # 'NR_PT'
        
        self.vs = vertical['SCALE']       # 'SCALE' - [unit] / div
        self.vo = vertical['OFFSET']      # 'OFFSET' - [unit]
        self.vp = vertical['POSITION']    # 'POSITION' - [div]
        self.vu = vertical['UNITS']       # 'UNITS' - [unit]
         
# =============================================================================
#         # Extract parameters from the channel preamble
#         self.vs = ch_pre['SCALE']       # 'SCALE' - [unit] / div
#         self.vo = ch_pre['OFFSET']      # 'OFFSET' - [unit]
#         self.vp = ch_pre['POSITION']    # 'POSITION' - [div]
#         self.hs = self.dt * self.np / 10.0
#         self.vu = ch_pre['UNITS']       # 'UNITS' - [unit]
# =============================================================================

    def __len__(self):
        return len(self.data)
        
    def getRaw(self):
        return self.data

    def getRealDiv(self):
        return self.getReal() / self.vert['SCALE'] + self.vert['POSITION']

    def getReal(self, variant='new'):
        if variant == 'new':
            return self.data * self.wfm['YMULT'] + self.wfm['YZERO']
        else:
            return (self.data - self.wfm['YOFF']) * self.wfm['YMULT']
        
    def getTimeBase(self):
        return self.wfm['XINCR'] * np.arange(np.size(self.data))

    def getSaturation(self):
        us = self.vert['SCALE'] * (5 - self.vert['POSITION'])
        ls = - self.vert['SCALE'] * (5 + self.vert['POSITION'])
        return (ls,  us)

    def getRange(self):
        y = self.getReal()
        ymin = np.min([np.min(y),  0])
        ymax = np.max([np.max(y),  0])
        return (ymin,  ymax)
    
    def getDt(self):
        return self.wfm['XINCR']
    

# class WaveformAVG(Waveform):
#     def __init__(self, parrent=None, avglen):
#         self.avglen = avglen
#         self.buffer = deque(maxlen=self.avglen)
#         super().__init__(parrent)
        

class Channel:
# =============================================================================
#     def __init__(self,  instr,  num,  ch_pre):
#         self.instr = instr
#         self.number = num
#         
#         # TODO: FIX this !!
#         self.offset = float(ch_pre[3])      # 'OFFSET'
#         self.invert = bool(ch_pre[4])       # 'INVERT'
#         self.position = float(ch_pre[5])    # 'POSITION'
#         self.scale = float(ch_pre[6])       # 'SCALE'
#         self.termination = float(ch_pre[7]) # 'TERMINATION'
#         self.probe = Probe(ch_pre[9:14])
# 
#         # List of nominal scales
#         self.vscales = np.array([1e-3,  2e-3,  5e-3,  1e-2,  2e-2,  5e-2,  1e-1,  2e-1,  5e-1,  1,  2,  5,  10])
#         self.vscales = self.vscales / self.probe.gain
# 
# =============================================================================

    def __init__(self,  instr,  num):
        self.instr = instr
        self.number = num
        
        # List of nominal scales
        self.vscales = np.array([5e-4, 1e-3,  2e-3,  5e-3,  1e-2,  2e-2,  5e-2,  1e-1,  2e-1,  5e-1,  1,  2,  5,  10])
        
        ch_str = 'CH{:d}:'.format(num)
        self.ch_str = ch_str
        
        self.update()


    def __str__(self):
        string = '==== Channel ' + str(self.number) + ' ====\n' \
                 'Offset:       ' + str(self.offset) + '\n' \
                 'Inverted:     ' + str(self.invert) + '\n' \
                 'Position:     ' + str(self.position) + '\n' \
                 'Scale:        ' + str(self.scale) + '\n' \
                 'Termination:  ' + str(self.termination) + '\n' \
                 '---- Probe ----\n' + str(self.probe) + '---------------\n'

        return string


    def vScaleUp(self):
#        nom = self.scale * self.probe.gain
        nom = self.scale

        # Switch to the higher scale if possible
        if nom < self.vscales[-1]:
            new = self.vscales[self.vscales > nom][0]
            self.instr.write('CH{:d}:SCAle {:.0e}'.format(self.number,  new))
            while bool(self.instr.query_ascii_values('BUSY?')[0]):
                pass;
            ret = self.instr.query_ascii_values('CH{:d}:SCAle?'.format(self.number))[0]
            if ret != new:
                print('current = {:.1e},  target = {:.1e}'.format(ret,  new))
            else:
                self.scale = ret
        else:
            print('Scale at maximum')

    def vScaleDown(self):
#        nom = self.scale * self.probe.gain
        nom = self.scale

        # Switch the lower scale if possible
        if nom > self.vscales[0]:
            new = self.vscales[self.vscales < nom][-1]
            self.instr.write('CH{:d}:SCAle {:.0e}'.format(self.number,  new))
            while bool(self.instr.query_ascii_values('BUSY?')[0]):
                time.sleep(.2)
            ret = self.instr.query_ascii_values('CH{:d}:SCAle?'.format(self.number))[0]
            if ret != new:
                print('current = {:d},  target = {:d}'.format(ret,  new))
            else:
                self.scale = ret
        else:
            print('Scale at minimum')

    def setVPosition(self,  vpos):
        if vpos > 5: self.vp = 5
        elif vpos < -5: self.vp = -5
        else: self.vp = vpos
        self.instr.write('CH{:d}:POSition {:.2f}'.format(self.number,  self.vp))
        return self.vp

    def readWaveform(self):
        pass
    
    def getOffset(self):
        return self.instr.query_ascii_values(self.ch_str + 'offset?')[0]
     
    def getScale(self):
        return self.instr.query_ascii_values(self.ch_str + 'scale?')[0]
    
    def getPosition(self):
        return self.instr.query_ascii_values(self.ch_str + 'position?')[0]

    def update(self):
        ch_pre = {
            'OFFSET': self.instr.query_ascii_values(self.ch_str + 'offset?')[0],
            'INVERT': self.instr.query_ascii_values(self.ch_str + 'invert?')[0],
            'POSITION': self.instr.query_ascii_values(self.ch_str + 'position?')[0],
            'SCALE': self.instr.query_ascii_values(self.ch_str + 'scale?')[0],
            'TERMINATION': self.instr.query_ascii_values(self.ch_str + 'termination?')[0],
            'UNITS': self.instr.query(self.ch_str + 'PROBE:UNITS?').translate({ord(c): None for c in '"\r\n'})
        }
        
        probe_str = self.ch_str + 'probe:'
        probe_fields = {
            'GAIN': self.instr.query_ascii_values(probe_str + 'gain?')[0],
            'RESISTANCE': self.instr.query_ascii_values(probe_str + 'resistance?')[0],
            'UNITS': self.instr.query(probe_str + 'units?').translate({ord(c): None for c in '"\r\n'}),
            'ID:TYPE': self.instr.query(probe_str + 'id:type?').translate({ord(c): None for c in '"\r\n'}),
            'SERNUMBER': self.instr.query(probe_str + 'id:sernumber?').translate({ord(c): None for c in '"\r\n'})
        }

        self.offset = ch_pre['OFFSET']      # 'OFFSET'
        self.invert = ch_pre['INVERT']       # 'INVERT'
        self.position = ch_pre['POSITION']    # 'POSITION'
        self.scale = ch_pre['SCALE']       # 'SCALE'
        self.termination = ch_pre['TERMINATION'] # 'TERMINATION'
        self.probe = Probe(probe_fields)

        if self.probe.id in passive_probes:
            self.vscales = self.vscales / self.probe.gain
        else:
            if self.probe.id in known_probes.keys():
                forced_range = self.instr.query_ascii_values(self.ch_str + 'PRObe:FORCEDRange?')[0]
                self.vscales = known_probes[self.probe.id][forced_range]





def readMultiWave(fname,  oldFormat=True):
    with open(fname,  'rt',  newline='\r\n') as file:
        lines = file.read().splitlines()
        num = len(lines[0].split(',')) - 1

        # Read the channel preamble
        data = [[] for i in range(num)]
        for i in range(num):
            data[i].append(int(lines[0].split(',')[i + 1][-1]))

        fields = [[] for i in range(num)]
        for i in range(8):
            row = lines[i + 1].split(',')
            for j in range(num):
                if i == 6: fields[j].append(row[j + 1])
                else: fields[j].append(float(row[j + 1]))

        y = np.array([[int(x) for x in line.split(',')[1:]] for line in lines[9:]])
        for i in range(num):
            data[i].append(fields[i])
            data[i].append(y[:,  i])

        return data

def rawToReal(chdata):
    return (chdata[2] - chdata[1][5]) * chdata[1][4]

def readTekData(fname):
    with open(fname,  'rt',  newline='\r\n') as file:
        lines = file.read().splitlines()

        # Get the number of samples
        n = int(lines[0].split(", ")[1])

        # Get the sampling interval
        dt = float(lines[1].split(", ")[1])

        # Get the trigger point index
        tp = int(lines[2].split(", ")[1])

        # Load the data samples
        y = np.empty(n)
        for i in range(n):
            y[i] = float(lines[i].split(", ")[-1])

        return [dt,  tp,  y]

def dumpObject(data,  fname):
    if os.path.exists(fname):
        raise FileExistsError('Filename already exists')

    if not os.path.exists(os.path.dirname(fname)):
        try:
            os.makedirs(os.path.dirname(fname))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(fname,  'wb') as file:
        pickle.dump(data,  file)
        print('Waveform saved.')


def readMultiWaveMSO6(fname, start=11):
    data = {}

    with open(fname, mode='r') as file:
        lines = file.read().splitlines()
        keys = [key for key in lines[start].split(',')]
        for key in keys:
            data[key] = np.empty(len(lines) - start - 1)
        for i, line in enumerate(lines[start + 1:]):
            ldata = line.split(',')
            for j, key in enumerate(keys):
                data[key][i] = ldata[j]

    return data

def plotWaveform(wfms):
    if not isinstance(wfms, list):
        wfms = [wfms]
        fig,  axs = plt.subplots(1,  1,  figsize=(12,  10))
        axs = [axs]
    else:
        fig,  axs = plt.subplots(1,  len(wfms),  figsize=(12,  10))
        if len(wfms) == 1: axs = [axs]

    for i,  wfm in enumerate(wfms):
        y = wfm.getReal()
        t = wfm.getTimeBase()

        # us = wfm.vs * (5 - wfm.vp)
        # ls = -wfm.vs * (5 + wfm.vp)

        axs[i].plot(t * 1e6,  y)
        # axs[i].axhline(y=us,  linestyle='--',  color='k',  linewidth=0.8)
        # axs[i].axhline(y=ls,  linestyle='--',  color='k',  linewidth=0.8)
        # axs[i].set_ylim((-10 * wfm.vs,  10 * wfm.vs))
        # axs[i].set_yticks(np.linspace(-10 * wfm.vs,  10 * wfm.vs,  21))
        axs[i].grid()

    plt.show()
