#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ***************************************************************************
# *   Copyright (C) 2011, Paul Lutus                                        *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program; if not, write to the                         *
# *   Free Software Foundation, Inc.,                                       *
# *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
# ***************************************************************************

import math

class BiquadState():
    b0 = b1 = b2 = a1 = a2 = 0.0
    x1 = x2 = y1 = y2 = 0.0
    d1 = d2 = 0.0
    
class Biquad:
  
    # pretend enumeration
    LOWPASS, HIGHPASS, BANDPASS, NOTCH, PEAK, LOWSHELF, HIGHSHELF = range(7)
    
    def __init__(self, typ, freq, srate, Q, dbGain=0, df2=False, lastFilter=None):
        #DF2 does NOT like chaning of constants
        types = {
            Biquad.LOWPASS : self.lowpass,
            Biquad.HIGHPASS : self.highpass,
            Biquad.BANDPASS : self.bandpass,
            Biquad.NOTCH : self.notch,
            Biquad.PEAK : self.peak,
            Biquad.LOWSHELF : self.lowshelf,
            Biquad.HIGHSHELF : self.highshelf
        }
        assert(types.has_key(typ))
        freq = float(freq)
        self.srate = float(srate)
        Q = float(Q)
        dbGain = float(dbGain)
        self.a0 = self.a1 = self.a2 = 0
        self.b0 = self.b1 = self.b2 = 0
        
        if lastFilter:
            lastState = lastFilter.state
            self.x1 = lastState.x1
            self.x2 = lastState.x2
            self.y1 = lastState.y1
            self.y2 = lastState.y2
            self.d1 = lastState.d1
            self.d2 = lastState.d2
        else:
            self.x1 = self.x2 = 0
            self.y1 = self.y2 = 0
            self.d1 = self.d2 = 0
            
        # only used for peaking and shelving filter types
        A = math.pow(10, dbGain / 40)
        omega = 2 * math.pi * freq / self.srate
        sn = math.sin(omega)
        cs = math.cos(omega)
        alpha = sn / (2 * Q)
        beta = math.sqrt(A + A)
        types[typ](A, omega, sn, cs, alpha, beta)
        
        # prescale constants
        self.b0 /= self.a0
        self.b1 /= self.a0
        self.b2 /= self.a0
        self.a1 /= self.a0
        self.a2 /= self.a0
        
        self.state = BiquadState()
        self.state.b0 = self.b0
        self.state.b1 = self.b1
        self.state.b2 = self.b2
        self.state.a1 = self.a1
        self.state.a2 = self.a2
        
        self.df2 = df2

    def lowpass(self, A, omega, sn, cs, alpha, beta):
        self.b0 = (1 - cs) / 2
        self.b1 = 1 - cs
        self.b2 = (1 - cs) / 2
        self.a0 = 1 + alpha
        self.a1 = -2 * cs
        self.a2 = 1 - alpha
    
    def highpass(self, A, omega, sn, cs, alpha, beta):
        self.b0 = (1 + cs) / 2
        self.b1 = -(1 + cs)
        self.b2 = (1 + cs) / 2
        self.a0 = 1 + alpha
        self.a1 = -2 * cs
        self.a2 = 1 - alpha
    
    def bandpass(self, A, omega, sn, cs, alpha, beta):
        self.b0 = alpha
        self.b1 = 0
        self.b2 = -alpha
        self.a0 = 1 + alpha
        self.a1 = -2 * cs
        self.a2 = 1 - alpha
    
    def notch(self, A, omega, sn, cs, alpha, beta):
        self.b0 = 1
        self.b1 = -2 * cs
        self.b2 = 1
        self.a0 = 1 + alpha
        self.a1 = -2 * cs
        self.a2 = 1 - alpha
    
    def peak(self, A, omega, sn, cs, alpha, beta):
        self.b0 = 1 + (alpha * A)
        self.b1 = -2 * cs
        self.b2 = 1 - (alpha * A)
        self.a0 = 1 + (alpha / A)
        self.a1 = -2 * cs
        self.a2 = 1 - (alpha / A)
    
    def lowshelf(self, A, omega, sn, cs, alpha, beta):
        self.b0 = A * ((A + 1) - (A - 1) * cs + beta * sn)
        self.b1 = 2 * A * ((A - 1) - (A + 1) * cs)
        self.b2 = A * ((A + 1) - (A - 1) * cs - beta * sn)
        self.a0 = (A + 1) + (A - 1) * cs + beta * sn
        self.a1 = -2 * ((A - 1) + (A + 1) * cs)
        self.a2 = (A + 1) + (A - 1) * cs - beta * sn
    
    def highshelf(self, A, omega, sn, cs, alpha, beta):
        self.b0 = A * ((A + 1) + (A - 1) * cs + beta * sn)
        self.b1 = -2 * A * ((A - 1) + (A + 1) * cs)
        self.b2 = A * ((A + 1) + (A - 1) * cs - beta * sn)
        self.a0 = (A + 1) - (A - 1) * cs + beta * sn
        self.a1 = 2 * ((A - 1) - (A + 1) * cs)
        self.a2 = (A + 1) - (A - 1) * cs - beta * sn
      
    # perform filtering function
    def __call__(self, x):
        '''
        r1 = self.applyBiQuadFilterDf2T(x)
        r2 = self.applyBiquadFilter(x)
        
        assert (r2-r1) < 0.000000000001
        return r1
        '''

        if self.df2:
            return self.applyBiQuadFilterDf2T(x)
        else:
            return self.applyBiquadFilter(x)

    def applyBiquadFilter(self, x):
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2, self.x1 = self.x1, x
        self.y2, self.y1 = self.y1, y
        self.state.x1 = self.x1
        self.state.x2 = self.x2
        self.state.y1 = self.y1
        self.state.y2 = self.y2
        return y
        
    def applyBiQuadFilterDf2T(self, sample):
        '''compute result'''
        result = self.b0 * sample + self.d1       
        self.d1 = self.b1 * sample - self.a1 * result + self.d2       
        self.d2 = self.b2 * sample - self.a2 * result
        self.state.d1 = self.d1
        self.state.d2 = self.d2
        return result
    
    # provide a static result for a given frequency f
    def result(self, f):
        phi = (math.sin(math.pi * f * 2 / (2.0 * self.srate))) ** 2
        return ((self.b0 + self.b1 + self.b2) ** 2 - \
        4 * (self.b0 * self.b1 + 4 * self.b0 * self.b2 + \
        self.b1 * self.b2) * phi + 16 * self.b0 * self.b2 * phi * phi) / \
        ((1 + self.a1 + self.a2) ** 2 - 4 * (self.a1 + \
        4 * self.a2 + self.a1 * self.a2) * phi + 16 * self.a2 * phi * phi)

    def log_result(self, f):
        try:
            r = 10 * math.log10(self.result(f))
        except:
            r = -200
        return r

    # return computed constants
    def constants(self):
        return self.b0, self.b1, self.b2, self.a1, self.a2
    
