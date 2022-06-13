# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 17:21:24 2017

@author: Elyse Barre
"""

import visa
#import sys
import time
#import numpy as np


class Controller():
    def __init__(self, port='COM3'):
        rm = visa.ResourceManager()
        self.instr = rm.open_resource(port, read_termination='\r', write_termination = '\r')
        self.instr.write('COMP 0')
        if not(int(self.instr.read())==0):
            print('Write to Standard Command Protocol unsuccessful')
        self.instr.write('PS 0, 0') #set absolute position to zero
        if not(int(self.instr.read())==0):
            print('Reseing aboslute position to zero was unsuccessful')
        
    
    def getBaud(self):
        return self.instr.query('BAUD')
        
        
    def ID(self ):
        self.instr.write('?')
        time.sleep(0.1)
        response = self.instr.read()
        if response =='':
            return None
        while not 'END' in response:
            response.append(self.instr.read())
        return response

        
    def reset(self):
        res = self.instr.query('RESET')
        if not (int(res) == 0):
            print('Reset was unsuccesful')
            
        
    def close(self):
        #self.reset()
        self.instr.close()
    
    def Move(self,x,y): #should move a relative distance
        result = self.instr.query('GR '+str(x)+', '+str(y))
        return result
    
    def goAbsolute(self,x,y):
        result = self.instr.query('G '+str(x)+', '+str(y))
        return result

    
    def set_resolution(self,res): #res in microns
        #S may need to be changed to X and then repeated with Y
        self.instr.write('RES,S, '+str(res)) 
    
    def Position(self): #this should return the position relative to the original position when you added the prior controller
        result = self.instr.query('P') 
        #Result is returned as x,y,z, this needs to be parsed, I think you can probably use result.split(",");
        return result
    
    def Pattern(self, take_data, nx, ny, dx, dy, mode='snake'):
        for j in range(ny):
            for i in range(nx):
                #if j is even, move along +x, if j is odd, move along -x
                direction = 2 * (j % 2) - 1
                try:
                    take_data(i,j)
                    print('points taken:', j%2*(nx-1)-direction*i, j)
                except:
                    print('data taking failed')

                self.Move(direction*dx, 0)
            self.Move(0, dy)
    def Linecut(self, take_data, axis, num, d):
        direction = 0
        if axis=='y':
            direction = 1
        for i in range(num):
            try:
                take_data()
                print('points taken', i)
            except:
                print('data taking failed')
            self.Move((1-direction)*d, direction*d)