
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 18:10:37 2017

@author: Elyse Barre
"""

import visa
import sys
import time
import numpy as np


class SR830:
    def __init__(self, port='GPIB0::11::INSTR'):
        rm = visa.ResourceManager()
        try:
            self.instr = rm.open_resource(port)
            self.instr.clear()
        except:
            print('Intrument unavailable. Available instruments:')
            resources = rm.list_resources()
            for item in resources:
                print(item)
            sys.exit()
        self.tconst_opt = {0 : 10e-6,
           1 : 30e-6,
           2 : 100e-6,
           3 : 300e-6,
           4 : 1e-3,
           5 : 3e-3,
           6 : 10e-3,
           7 : 30e-3,
           8 : 100e-3,
           9 : 300e-3,
           10: 1,
           11: 3,
           12: 10,
           13: 30,
           14: 100,
           15: 300,
           16: 1000,
           17: 3000,
           18: 10000,
           19: 30000
        } 
        self.sens_opt = {0 : '2 nV/fA',
           1 : '5 nV/fA',
           2 : '10 nV/fA',
           3 : '20 nV/fA',
           4 : '50 nV/fA',
           5 : '100 nV/fA',
           6 : '200 nV/fA',
           7 : '500 nV/fA',
           8 : '1 uV/pA',
           9 : '3 uV/pA',
           10: '5 uV/pA',
           11: '10 uV/pA',
           12: '20 uV/pA',
           13: '50 uV/pA',
           14: '100 uV/pA',
           15: '200 uV/pA',
           16: '500 uV/pA',
           17: '1 mV/nA',
           18: '2 mV/nA',
           19: '5 mV/nA',
           20: '10 mV/nA',
           21: '20 mV/nA',
           22: '50 mV/nA',
           23: '100 mV/nA',
           24: '200 mV/nA',
           25: '500 mV/nA',
           26: '1V/uA'
        } 
                
    def id_instr(self):
        return self.instr.query('*IDN?')
    
            
    def send_command(self, command):
        response = self.instr.write(command)
        time.sleep(.1)
        if response != '':
            return response
        else:
            return None   
            
    def get_response(self, command):
        self.instr.clear()
        response = self.instr.query(command)
        if response != '':
            return response
        else:
            return None
            
    def reset(self):
        self.instr.query('*RST')
            
    def close(self):
        self.instr.clear()
        self.instr.close()
        
        
    def getsens(self):
        """
        The SENS? command queries the sensitivity.
        """
        i = self.get_response('SENS?')
        return self.sens_opt[int(i)]
        
    def setsens(self,i):
        """
        The SENS command sets the sensitivity.
        """
        if type(i)==int and i>=0 and i<=26:
            self.send_command('SENS '+str(i))
            newsens = int(self.get_response('SENS?'))
            if newsens is not i:
                print('Failed to set sensitivity. Instead reading'+str(newsens))
        else:
            print('Sensitivity is given as an integer as follows:')
            print(self.sens_opt)
            
    def getphase(self):
        """
        The PHAS? command queries the phase.
        """
        i = self.get_response('PHAS?')
        return float(i)
        
    def setphase(self,i):
        """
        The PHAS command sets the phase.
        """
        if (type(i)==int or type(i) == float):
            self.send_command('PHAS '+str(i))
            try:
                newphase = float(self.get_response('PHAS?').rstrip())
            except:
                print('Setting Phase failed')
                print(self.sens_opt)
            #if newphase is not i:
            #    print('Failed to set phase')
        else:
            print('Please use a integer of float for phase')
            print(self.sens_opt)
            

    def getX(self):
        return float(self.get_response('OUTP? 1'))
        
    def getY(self):
        return float(self.get_response('OUTP? 2'))
        
    def getXY(self):
        xstr, ystr = self.get_response('SNAP?1,2').rstrip().split(',')
        x = float(xstr)
        y = float(ystr)
        return x,y
        
    def getR(self):
        return float(self.get_response('OUTP? 3'))
    
    def getTheta(self):
        return float(self.get_response('OUTP? 4'))
        
    def getTC(self):
        """
        The OFLT? command queries the TC.
        """
        i = self.get_response('OFLT?')
        return self.tconst_opt[int(i)]
        
    def setTC(self,i):
        """
        The OFLT command sets the TC
        .
        """
        if type(i)==int and i>=0 and i<=26:
            self.send_command('OFLT '+str(i))
            newTC = int(self.get_response('OFLT?'))
            if newTC is not i:
                print('Failed to set time constant')
        else:
            print('Time constant is given as an integer as follows:')
            print(self.tconst_opt)
            
    def set_coupling(self,coup):
        if coup == 'AC' or coup == 'ac':
            self.send_command('ICPL 0')
        elif coup == 'DC' or coup == 'dc':
            self.send_command('ICPL 1')
        else:
            print('Only have AC or DC coupling \n')
    
    def get_coupling(self):
        resp = float(self.get_response('ICPL?').rstrip()) 
        if resp==0:
            print('AC')
        else:
            print('DC')
    
    def get_input_config(self):
        resp = float(self.get_response('ISRC?').rstrip())
        if resp ==0:
            print('A')
        elif resp ==1:
            print('A-B')
        elif resp ==2:
            print('I(1e6)')
        elif resp ==3:
            print('I(1e9)')
            
    def set_input_config(self,i):
        self.send_command('ISRC '+str(i))
        resp = int(self.get_response('ISRC?').rstrip())
        if(resp is not i):
            print('Failed to set input configuration, instead find setting = '+ str(resp))

if __name__== '__main__':
    lockin = SR830()