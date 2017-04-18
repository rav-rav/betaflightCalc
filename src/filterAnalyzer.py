# -*- coding: utf-8 -*-
'''
Created on 20.03.2017

@author: rav
'''

import math

from onePoleFilter import OnePole
from biquad_module import Biquad
from filterResponse import biquadEval
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


SAMPLING_RATE = 1000
Q_BUTTERWORTH = 1.0 / np.sqrt(2)    #butterworth


def filterGetNotchQ(centerFreq, cutoff):
    octaves = np.log2(float(centerFreq) / cutoff) * 2
    return np.sqrt(np.power(2, octaves)) / (np.power(2, octaves) - 1)


def filterGetNotchQApprox(centerFreq, cutoff):
    centerFreq = float(centerFreq)
    cutoff = float(cutoff)
    return ((cutoff * centerFreq) / ((centerFreq - cutoff) * (centerFreq + cutoff)))


def getQs(order):
    '''
    So, our single Q value is based on the angle π/4; 1/(2cos(π/4)) 
    '''
    Qs = []
    if order % 2 == 0:
        angleSpacing = np.pi / 2.0 / order
    else:
        Qs.append(-1)
        angleSpacing = np.pi / order
        
    angle = angleSpacing
    i = 0
    while angle < np.pi / 2.0:
    #for a in range(order/2):
        Q = 1.0 / (2 * np.cos(angle))
        Qs.append(Q)
        
        if order % 2 == 0:
            angle += angleSpacing * 2
        else: 
            angle += angleSpacing
            
        i += 1
    return Qs


def getNotchFilter(centerFreq, cutoff):
    Q = filterGetNotchQ(centerFreq, cutoff)
    result = Biquad(Biquad.NOTCH, centerFreq, SAMPLING_RATE, Q)
    return result


def getLpfFilter(cutoff, Q = Q_BUTTERWORTH):
    return Biquad(Biquad.LOWPASS, cutoff, SAMPLING_RATE, Q)


def cascadeFilters(filters):
    # return the results for a filter cascade
    mags = []
    phases = []
    
    for filt in filters:
        magdB, phase = biquadEval(filt)
        mags.append(magdB)
        phases.append(phase)
    
    mags = np.vstack(mags)
    phases = np.vstack(phases)
    
    return mags, phases


if __name__ == '__main__':
    if 0:
        #test performance
        import time
        lpf = getLpfFilter(100, Q_BUTTERWORTH)
        start = time.time()
        for i in range(1000):
            biquadEval(lpf, 1000)
        print "duration", time.time() - start
        raise
    
    if 0:
        #delay differences for lpf filters with different orders and frequencies
        maxPlotFreq = 200
        legend = []
        
        plt.title("LPF")
        plt.xlabel("Hz")
        plt.ylabel("ms / dB")
        
        for order in range(2, 3):
            print "order=%i" % order
            
            for freq in range(220, 301, 10):
                print "freq=%i" % freq
                legend.append("%iHz" % freq)
                Qs = getQs(order)
                phases = []
                mags = []
                
                for Q in Qs:
                    if Q == -1:
                        lpf = OnePole(SAMPLING_RATE, freq)
                    else:
                        lpf = getLpfFilter(freq, Q)
                    
                    magdB, phase = biquadEval(lpf)
                    magdB = magdB[:maxPlotFreq]
                    phase = phase[:maxPlotFreq]

                    mags.append(magdB)
                    phases.append(phase)
                
                #plot magnitude and phase
                plt.plot(np.sum(np.vstack(mags), axis = 0))
                plt.plot(np.sum(np.vstack(phases), axis = 0))

        plt.legend(legend)
        plt.show()
        
    if 0:
        #delay differences for notch filters with different center and cutoff
        legend = []
        maxPlotFreq = 200

        fig = plt.figure()
        ax = Axes3D(fig)
        
        plt.title("notch delay")
        plt.xlabel("Hz")
        plt.ylabel("ms / dB")
        
        for centerFreq in range(160, 301, 10):
            for width in range(30, 151, 10):
                cutoff = max(centerFreq - width, 100)
                print "centerFreq=%i, cutoff=%i" % (centerFreq, cutoff)
                nf = getNotchFilter(centerFreq, cutoff)
                magdB, phase = biquadEval(nf)
                magdB = magdB[:maxPlotFreq]
                phase = phase[:maxPlotFreq]
                #plt.plot(magdB)
                #plt.plot(phase)
                ax.plot([centerFreq]*len(phase), range(len(phase)), phase)
                #ax.scatter([centerFreq], [cutoff], [np.mean(phase)])

        plt.show()
    
    if 1:
        #different filter cascades
        filters = []
        if 1:
            #classical filter setup
            filters.append(getLpfFilter(100))
            filters.append(getNotchFilter(275, 160))
            filters.append(getNotchFilter(320, 240))
            
            #d is filtered more
            filters.append(getLpfFilter(100))
            filters.append(getNotchFilter(280, 160))
    
    
        elif 1:
            #higher lowpass, more notch
            filters.append(getLpfFilter(120))
            filters.append(getNotchFilter(390, 50))
            filters.append(getNotchFilter(390, 50))
            filters.append(getNotchFilter(390, 50))
            
    
        mags, phases = cascadeFilters(filters)
        magSum = np.sum(mags, axis = 0)
        phaseSum = np.sum(phases, axis = 0)
    
        for val in range(0, 150, 10):
            print "freq=%iHz, mag=%fdB, delay=%fms" % (val, magSum[val], phaseSum[val])
        
    
        plt.xlabel("Hz")        
        plt.ylabel("dB")        
        plt.plot(magSum)
        plt.plot(phaseSum)
        plt.ylim(-100, 10)
        plt.legend(["magnitude", "phase"])
        plt.show()
        