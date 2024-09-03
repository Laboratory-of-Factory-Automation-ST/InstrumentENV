import time
import tektronix
import numpy as np

class ScopeTest:
    def __init__(self,  instr=None):
        self.wfm_initialized = False
        self.instr = instr
        self.max_rec_length = 2e6
        self.channels = []
        self.id = ''

        if instr != None:
            self.connectResource(instr)

    def __str__(self):
        string = self.id + '\n'
        for channel in self.channels:
            string += str(channel)

        return string
    
    def isConnected(self):
        return self.instr is not None
    
    def getChPreamble(self, num):
        ch_str = 'CH{:d}:'.format(num)
        ch_pre = {
            'OFFSET': self.instr.query_ascii_values(ch_str + 'offset?')[0],
            'INVERT': self.instr.query_ascii_values(ch_str + 'invert?')[0],
            'POSITION': self.instr.query_ascii_values(ch_str + 'position?')[0],
            'SCALE': self.instr.query_ascii_values(ch_str + 'scale?')[0],
            'TERMINATION': self.instr.query_ascii_values(ch_str + 'termination?')[0],
            'UNITS': self.instr.query(ch_str + 'PROBE:UNITS?').translate({ord(c): None for c in '"\r\n'})
        }
        
        return ch_pre
    
    
    def getVerticalSettings(self, channel):
        vertical = {
            'OFFSET': self.instr.query_ascii_values(channel + ':offset?')[0],
            'POSITION': self.instr.query_ascii_values(channel + ':position?')[0],
            'SCALE': self.instr.query_ascii_values(channel + ':scale?')[0],
            'UNITS': self.instr.query(channel + ':PROBE:UNITS?').translate({ord(c): None for c in '"\r\n'})
        }
        return vertical

    def wfmTransferConfig(self):
        # First set the encoding of the transferred data.
        # Binary: LSB to MSB
        self.instr.write('DATa:ENCdg SRIBinary')

        # Set the size of each point in the waveform to 2 bytes.
        self.instr.write('WFMOutpre:BYT_Nr 2')

        # Set the maximum length of the record to include the whole waveform
        self.instr.write('DATa:STARt 1')
        self.instr.write('DATa:STOP 100e6')

        self.wfm_initialized = True

    def setResource(self,  instr):
        # assign the instrument instance and set the read/write termination
        self.instr = instr
        self.instr.read_termination = '\n'
        self.instr.write_termination = '\n'
        self.instr.encoding = 'utf8'

        self.id = self.instr.query('*IDN?')
        self.instr.write('header off')

    def connectResource(self,  instr):
        # Configure the resource and waveform transfer
        self.setResource(instr)
        self.wfmTransferConfig()

        # Update information about all channels
        for i in range(6):
            self.channels.append(tektronix.Channel(self.instr,  i + 1))
            
    def disconnectResource(self):
        self.wfm_initialized = False
        self.instr = None
        self.max_rec_length = 2e6
        self.channels = []
        self.id = ''

    def readWaveforms(self,  channels):
        # channels - list of strings describing the channel numbers or references
        ret = []

        if self.wfm_initialized == False:
            self.wfmTransferConfig()

        for ch in channels:
            # Select the waveform source
            self.instr.write('DATa:SOUrce {:s}'.format(ch))

            # Read the waveform and the channel preamble
            
            self.instr.write('header on')
            wfm_pre = self.instr.query('WFMOutpre?')
            self.instr.write('header off')
            # ch_pre = self.getChPreamble(ch)
            
            ## TODO: Query channel vertical scale and pass it to the waveform
            ## constructor
            vertical = self.getVerticalSettings(ch)

            # Transfer the waveform from the instrument
            data = self.instr.query_binary_values('CURVe?',  datatype='h',  container=np.array)

            # Create the Waveform from the red data
            wfm = tektronix.Waveform(tektronix.parseWFMPreamble(wfm_pre), vertical, data)
            ret.append(wfm)

        return ret

    def readWaveform(self,  channel):
        if self.wfm_initialized == False:
            self.wfmTransferConfig()

        # Select the waveform source
        self.instr.write('DATa:SOUrce {:s}'.format(channel))

        # Read the waveform and the channel preamble
        self.instr.write('header on')
        wfm_pre = self.instr.query('WFMOutpre?')
        self.instr.write('header off')
        # ch_pre = self.getChPreamble(channel)
        
        ## TODO: Query channel vertical scale and pass it to the waveform
        ## constructor
        vertical = self.getVerticalSettings(channel)

        # Transfer the waveform from the instrument
        data = self.instr.query_binary_values('CURVe?',  datatype='h',  container=np.array)

        # Create the Waveform from the red data
        wfm = tektronix.Waveform(tektronix.parseWFMPreamble(wfm_pre), vertical, data)

        return wfm

    def verticalAdjust(self, chlist, res=5000, fast=False):
        scaled = False

        # Store the actual resolution and set a lower one for faster data transfer
        # oldres = self.instr.query_ascii_values('HORizontal:RESOlution?')[0]
        # self.instr.write('HORizontal:RESOlution {:d}'.format(res))

        for ch in chlist:
            print('=====> Aligning ' + ch + '...')
            
            i = 0
            while not scaled:
                time.sleep(0.1)
                i += 1              # Count number of iterations
                print('  --[ Iteration {:d} ]--'.format(i))

                self.waitForTrigger()
                wfm = self.readWaveform(ch)
                y = wfm.getReal()
                vp = self.getChannel(ch).getPosition()
                vs = self.getChannel(ch).getScale()
                su = - vp + 4.95   # Maybe add here some margin ie. 0.1 div
                sl = - vp - 4.95   # Maybe add here some margin ie. 0.1 div

                dmin = np.min([np.min(y), 0]) / vs
                dmax = np.max([np.max(y), 0]) / vs
                
                print('\t vert. position: {:.2f}'.format(vp))
                print('\t vert. scale: {:.2f}'.format(vs))
                print('\t upper sat.: {:.2f}'.format(su))
                print('\t lower sat.: {:.2f}'.format(sl))
                print('\t dmin: {:.2f}'.format(dmin))
                print('\t dmax: {:.2f}'.format(dmax))

                # TODO: Remove house numeros
                if dmax >= su and dmin <= sl:
                    self.getChannel(ch).vScaleUp()
                    print('\t Scaling up the channel.')
                elif dmax >= su:
                    # what to do if we cannot move the channel
                    if dmin - sl <= 0.5:
                        print('\t Scaling up the channel.')
                        self.getChannel(ch).vScaleUp()
                        continue

                    delta = dmin - sl
                    # position = vp - np.min([5 - vp, delta - 0.5])
                    position = vp - np.min([5 - vp, delta - 0.4])
                    self.instr.write('{:s}:POSition {:.3f}'.format(ch, position))
                    print('\t Changing the channel position.')
                elif dmin <= sl:
                    # what to do if we cannot move the channel
                    if su - dmax <= 0.5:
                        print('\t Scaling up the channel.')
                        self.getChannel(ch).vScaleUp()
                        continue

                    delta = su - dmax
                    # position = vp - np.min([5 + vp, - delta + 0.5])
                    position = vp - np.min([5 + vp, - delta + 0.4])
                    self.instr.write('{:s}:POSition {:.3f}'.format(ch, position))
                    print('\t Changing the channel position.')
                else:
                    # Add here some margin to overcome quantization noise issues
                    mindiv = 1.1 * vs * (dmax - dmin) / 10
                    optimal = self.getChannel(ch).vscales[self.getChannel(ch).vscales >= mindiv][0]
                    if round(vs, 5) > round(optimal, 5):
                        # Rounding the vertical scales to overcome false activation due to different FPN precisions
                        dmean = (dmax + dmin) / 2
                        self.instr.write('{:s}:POSition {:.3f}'.format(ch, - dmean))
                        if fast: self.instr.write('CH{:d}:SCAle {:.1e}'.format(ch, optimal))
                        else: self.getChannel(ch).vScaleDown()
                        print('\t Scaling down the channel.')
                    else:
                        dmean = (dmax + dmin) / 2
                        if np.abs(-dmean - vp) > 0.2:
                            self.instr.write('{:s}:POSition {:.3f}'.format(ch, - dmean))
                            
                        print('\t The scale and position are fine.\n')

                        # The scale is optimal, we are done.
                        break

        # Restore the original resolution
        # self.instr.write('HORizontal:RESOlution {:.2e}'.format(oldres))
        
    def getVerticalParams(self, chlist):

        # Store the actual resolution and set a lower one for faster data transfer
        # oldres = self.instr.query_ascii_values('HORizontal:RESOlution?')[0]
        # self.instr.write('HORizontal:RESOlution {:d}'.format(res))

        for ch in chlist:
            print('=====> Waveform vertical state of ' + ch + '...')
            wfm = self.readWaveform(ch)
            y = wfm.getReal()
            vp = self.getChannel(ch).getPosition()
            vs = self.getChannel(ch).getScale()
            su = - vp + 4.9   # Maybe add here some margin ie. 0.1 div
            sl = - vp - 4.9   # Maybe add here some margin ie. 0.1 div

            dmin = np.min([np.min(y), 0]) / vs
            dmax = np.max([np.max(y), 0]) / vs
            
            print('\t vert. position: {:.2f}'.format(vp))
            print('\t vert. scale: {:.2f}'.format(vs))
            print('\t upper sat.: {:.2f}'.format(su))
            print('\t lower sat.: {:.2f}'.format(sl))
            print('\t dmin: {:.2f}'.format(dmin))
            print('\t dmax: {:.2f}'.format(dmax))

# TODO: Throw en exception when timed out
    def waitForTrigger(self,  timeout=200,  verbose=False):
        laststate = int(self.instr.query_ascii_values('ACQuire:NUMACq?')[0])
        while True:
            time.sleep(.1)
            newstate = int(self.instr.query_ascii_values('ACQuire:NUMACq?')[0])
            if newstate > laststate:
                break
            if newstate < laststate:
                laststate = newstate
                continue
            timeout -= 1
            if timeout == 0:
                # print('Trigger timed out')
                return
        # print('\t\t\t Last state: {:d}'.format(laststate))
        # print('\t\t\t New state: {:d}'.format(newstate))
        if verbose:
            print('\t\t\t Triggered')
            
    def trigger(self):
        self.instr.write('TRIGger')

    def waitForAcquisition(self,  target):
        numacq = -1
        while numacq < target:
            numacq = int(self.instr.query_ascii_values('ACQuire:NUMACq?')[0])
            time.sleep(.1)

    def getChannel(self,  chnum):
        chnum = int(chnum[-1])
        return self.channels[chnum - 1]

    def readChannelSettings(self,  chnum):
#        return self.instr.query('CH{:d}?'.format(chnum)).split(';')
        return tektronix.parsePreamble(self.instr.query('CH{:d}?'.format(chnum)))

    def debugOutput(self,  command):
        self.instr.write('header on')
        fields = self.instr.query(command).split(';')
        for i,  elem in enumerate(fields):
            print('{:3d} - {:s}'.format(i,  elem))
        self.instr.write('header off')

    def update(self):
        for channel in self.channels:
            channel.update()

    def isBusy(self):
        return bool(self.instr.query_ascii_values('BUSY?')[0])
    
    def configureDPT(self):
        # Set the number of acquisitions for the averaging
        self.instr.write('ACQuire:NUMAVg 32')
        time.sleep(.1)
        # Set the trigger mode
        self.instr.write('TRIGger:A:MODe NORMal')
        time.sleep(.1)
        # Set pulse trigger source
        # self.instr.write('TRIGger:A:PULse:SOUrce CH1')
        # time.sleep(.1)
        # Set pulse trigger level
        self.instr.write('TRIGger:A:LEVel:CH1 200.0')
        time.sleep(.1)
        # Set pulse trigger high limit
        self.instr.write('TRIGger:A:PULse:WIDth:HIGHLimit 200.0E-6')
        time.sleep(.1)
        # Set pulse trigger low limit
        self.instr.write('TRIGger:A:PULse:WIDth:LOWLimit 100.0E-9')
        time.sleep(.1)
        # Set the trigger position
        self.instr.write('HORizontal:POSition 40')
        time.sleep(.1)
        # Set the horizontal record length
        self.instr.write('HORizontal:RECOrdlength 100000')
        time.sleep(.1)
        # Set the time base trigger
        self.instr.write('HORizontal:SCAle 200e-9')
        time.sleep(.1)