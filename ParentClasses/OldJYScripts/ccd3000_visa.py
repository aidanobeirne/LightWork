# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 21:52:14 2016

@author: heinz
"""

import numpy as np
import visa
import struct
#from spectra import SingleSpectrum


def initgpib():
    rm = visa.ResourceManager()

    ccd = rm.open_resource('GPIB0::6::INSTR')
    ccd.write_termination = ''
    return ccd

def packandwrite(ccd, data):
    buf = struct.pack('%sB' % len(data), *data)
    ccd.write_raw(buf)


# call this after the CCD controller is powered up. 
# this sequence appears to program the ccd in some way. it doesn't need to be repeated
# to reinitialize the CCD if GPIB connection is closed and reopened.
def initccd3000_visa():
    ccd = initgpib()
    
    ccd.read_termination = ''
    
    ccd.timeout = 1000
    reply = ccd.query(' ')
    if reply == 'B':
        newinitccd3000_visa(ccd)
    else:
        reinitccd3000_visa(ccd)
        
    return ccd
    
def newinitccd3000_visa(ccd):
    
    #print(reply) # B
    
    reply = ccd.query('O2000\x00')
    #print(reply) # *
    
    reply = ccd.query(' ')
    #print(reply) # F
    
    reply = ccd.query('z')
    print(reply) # oV1.90  CCD_3000IR\r
    
    reply = ccd.query('Z300,0\x0d')
    #print(reply) # o1\r
    
    
    
    ccd.read_termination = 'o'
    
    reply = ccd.query('Z340,0,0,53248,28\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i for i in range(1,28)] + [0])
    
    reply = ccd.query('Z340,0,1,53248,28\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(26)] + [0x0c, 0x08])
    
    reply = ccd.query('Z340,0,2,53248,28\x0d')
    #print(reply) # 'o'
    
    ccd.write('1111111111111100000000000000')
    
    reply = ccd.query('Z340,0,3,53248,28\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x01 for i in range(28)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,54272,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,600)] + [0])
    
    reply = ccd.query('Z340,0,1,54272,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(255)] + [0x09 for i in range(256)] + [0x0a for i in range(87)] + [0x0e, 0x08])
    
    reply = ccd.query('Z340,0,2,54272,600\x0d')
    #print(reply) # 'o'
    
    ccd.write('uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    
    reply = ccd.query('Z340,0,3,54272,600\x0d')
    #print(reply) # 'o'
    
    repeat = [0x01 for i in range(72)] + [0, 0, 0]
    packandwrite(ccd, [0x01 for i in range(57)] + [0, 0, 0] + repeat + repeat + repeat + repeat + repeat + repeat + repeat + [0x01 for i in range(15)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,55296,3\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd,[1,2,0])
    
    reply = ccd.query('Z340,0,1,55296,3\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd,[0x08,0x0c,0x08])
    
    reply = ccd.query('Z340,0,2,55296,3\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd,[0x30,0x30,0x30])
    
    reply = ccd.query('Z340,0,3,55296,3\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd,[1,1,1])

    
    
    
    
    reply = ccd.query('Z340,0,0,56320,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,600)] + [0])
    
    reply = ccd.query('Z340,0,1,56320,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(255)] + [0x09 for i in range(256)] + [0x0a for i in range(87)] + [0x0e, 0x08])
    
    reply = ccd.query('Z340,0,2,56320,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x31 for i in range(300)] + [0x30 for i in range(300)])
    
    reply = ccd.query('Z340,0,3,56320,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x01 for i in range(600)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,57344,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,600)] + [0])
    
    reply = ccd.query('Z340,0,1,57344,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(255)] + [0x09 for i in range(256)] + [0x0a for i in range(87)] + [0x0e, 0x08])
    
    reply = ccd.query('Z340,0,2,57344,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x31 for i in range(300)] + [0x30 for i in range(300)])
    
    reply = ccd.query('Z340,0,3,57344,600\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [1 for i in range(600)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,58368,300\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,300)] + [0])
    
    reply = ccd.query('Z340,0,1,58368,300\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(255)] + [0x09 for i in range(43)] + [0x0d, 0x08])
    
    reply = ccd.query('Z340,0,2,58368,300\x0d')
    #print(reply) # 'o'
    
    ccd.write('uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    
    reply = ccd.query('Z340,0,3,58368,300\x0d')
    #print(reply) # 'o'
    
    repeat = [0x01 for i in range(72)] + [0, 0, 0]
    packandwrite(ccd, [0x01 for i in range(57)] + [0, 0, 0] + repeat + repeat + repeat + [0x01 for i in range(15)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,59392,300\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,300)] + [0])
    
    reply = ccd.query('Z340,0,1,59392,300\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x08 for i in range(255)] + [0x09 for i in range(43)] + [0x0d, 0x08])
    
    reply = ccd.query('Z340,0,2,59392,300\x0d')
    #print(reply) # 'o'
    
    ccd.write('ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||pppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    
    reply = ccd.query('Z340,0,3,59392,300\x0d')
    #print(reply) # 'o'
    
    repeat = [0x01 for i in range(72)] + [0, 0, 0]
    packandwrite(ccd, [0x01 for i in range(57)] + [0, 0, 0] + repeat + repeat + repeat + [0x01 for i in range(15)])
    
    
    
    
    
    reply = ccd.query('Z340,0,0,60416,24\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [i%256 for i in range(1,24)] + [0])
    
    reply = ccd.query('Z340,0,1,60416,24\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [8,8,8,8,8,8,0,0,0,0,0,0,8,8,8,8,8,8,0,0,0,0,4,0])
    
    reply = ccd.query('Z340,0,2,60416,24\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x31 for i in range(12)] + [0x30 for i in range(12)])
    
    
    reply = ccd.query('Z340,0,3,60416,24\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x01 for i in range(24)])
    
    
    
    
    
    
    reply = ccd.query('Z340,0,6,53248,8192\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0 for i in range(8192)])
    
    
    reply = ccd.query('Z340,0,7,53248,8192\x0d')
    #print(reply) # 'o'
    
    packandwrite(ccd, [0x80 for i in range(8192)])
    
    
    
    
    
    reply = ccd.query('Z328,0,2,512,1,2,0,17,400,3,0,300,3,400000000,0,4,500,500,418,514\x0d')
    #print(reply) # 'o'
    
    ccd.read_termination = '\x0d'
    
    reply = ccd.query('z')
    #print(reply) # 'oV...\r'
    
    
    
    reply = ccd.query('Z303,0\x0d')
    #print(reply) # 'o0\r'
    
    reply = ccd.query('Z310,0\x0d')
    #print(reply) # 'o0,0,0,0,...\r'
    
    
    
    ccd.read_termination = 'o'
    reply = ccd.query('Z325,0,1,1\x0d')
    #print(reply) # 'o'
    
    reply = ccd.query('Z326,0,0,0,0,512,1,1,1\x0d')
    #print(reply) # 'o'
    
    ccd.read_termination = ''
    
    print('ccd3000_visa initialized')
    
    
# call this if GPIB is closed and reopened, but CCD controller has already been programmed with initccd()
def reinitccd3000_visa(ccd):
    #print(reply) # F
    
    reply = ccd.query(' ')
    #print(reply) # F
    
    reply = ccd.query('z')
    print(reply) # oV1.90  CCD_3000IR\r
    
    reply = ccd.query('Z303,0\x0d')
    #print(reply) # o0\r
    
    
    
    reply = ccd.query('z')
    #print(reply) # oV1.90  CCD_3000IR\r
    
    reply = ccd.query('Z303,0\x0d')
    #print(reply) # o0\r
    
    
    
    
    ccd.read_termination = '\x0d'
    
    reply = ccd.query('Z310,0\x0d')
    #print(reply) # o0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0\r
    
    
    ccd.read_termination = 'o'
    
    reply = ccd.query('Z325,0,1,1\x0d')
    #print(reply) # o
    
    reply = ccd.query('Z326,0,0,0,0,512,1,1,1\x0d')
    #print(reply) # o
    
    ccd.read_termination = ''
    print('ccd3000_visa initialized')
    
sleep_before_read = 0.8*1e-3
ccd3000_timeout = 1000
# this command sequence is required before any spectra are acquired. it sets the shutter delay and probably other capture
# parameters (presumably clean cycles, number active pixels, etc) which I haven't yet tried to decode.
# exposure is in milliseconds
def prepccd3000_visa(ccd, exposure):
    ccd.read_termination = 'o'
    
    reply = ccd.query('Z325,0,1,1\x0d')
    #print(reply) # 'o'
    
    reply = ccd.query('Z330,,0\x0d')
    #print(reply) # 'o'
    
    reply = ccd.query('Z305,0,1\x0d')
    #print(reply) # 'o'
    
    reply = ccd.query('Z305,0,1\x0d')
    #print(reply) # 'o'
    
    reply = ccd.query('Z326,0,0,0,0,512,1,1,1\x0d')
    #print(reply) # 'o'
    
    ccd.read_termination = '\x0d'
    reply = ccd.query('Z327,0\x0d')
    #print(reply) # o520,520\x0d
    
    
    ccd.read_termination = 'o'
    
    reply = ccd.query('Z301,0,%d\x0d' % exposure)
    #print(reply) # 'o'
    
    reply = ccd.query('Z331,0,%d\x0d' % exposure)
    #print(reply) # 'o'

    ccd3000_timeout = max(1000,exposure*2)
    ccd.timeout = ccd3000_timeout


# takes raw byte array and converts it to a numpy.array with only the live pixels
def unpackspectrum(raw):
    # real data starts at byte 5 (skip first byte and first 2 shorts).
    # after these bytes, the first short is pixel 256, second is pixel 0, third is 257, fourth is 1, ...
    # there are 13 bytes at end to be ignored.
    unpacked = np.array(struct.unpack('<512h',raw[5:(len(raw)-13)]))
    return np.concatenate((unpacked[1::2],unpacked[::2]))
    
    
# retrieves a single spectrum (actually collects two spectra, one dark and one with shutter open).
# result is returned as a SingleSpectrum.
def queryccd3000_visa(ccd):
    ccd.read_termination = 'o'
                      
    
    # collect with shutter open
    reply = ccd.query('Z311,0,1\x0d')  
    #print(reply) # 'o'
    
    ccd.read_termination = '\x0d'
    reply = ccd.query('Z312,0\x0d')
    #print(reply) # o0\r
    
    ccd.read_termination = ''
    
    ccd.write('Z315,0\x0d')
    #time.sleep(ccd3000_timeout*sleep_before_read)
    bright_counts = unpackspectrum(ccd.read_raw()) 
    
    return bright_counts+32768
    
