'''
Created on 12.04.2017

@author: rav
'''

import numpy as np

class OnePole():
    # single pole filter biquad style
    
    def __init__(self, samplingRate, fCenter):
        self.b0 = 1.0
        self.a1 = 0.0
        self.z1 = 0.0
        
        self.a1 = np.exp(-2.0 * np.pi * (float(fCenter) / samplingRate));
        self.b0 = 1.0 - self.a1
    
    def process(self, sample):
        self.z1 = sample * self.b0 + self.z1 * self.a1
        return self.z1
    
    def constants(self):
        return self.b0, 0, 0, -self.a1, 0

