'''
Created on 20.03.2017

@author: rav
'''

# http://www.earlevel.com/main/2016/12/01/evaluating-filter-frequency-response/ 
import numpy as np

# filter response, evaluated at numPoints from 0-pi, inclusive
def filterEval(zeros, poles, samplingRate, phaseShiftAsTime = True):
    numPoints = samplingRate / 2
    ws = np.arange(0, numPoints) *  np.pi / (numPoints - 1)

    resZeros = [[], [], []]
    resPoles = [[], [], []]
    for i in range(len(zeros)):
        resZeros[i] = zeros[i] * np.exp(-i * 1j * ws)
        resPoles[i] = poles[i] * np.exp(-i * 1j * ws)
        
    resZeros = np.sum(resZeros, axis = 0)
    resPoles = np.sum(resPoles, axis = 0)
    
    Hw = resZeros / resPoles
    mag = np.abs(Hw)
    mag[mag == 0] = 0.0000000001  # limit to -200 dB for log
        
    magdB = 20 * np.log10(mag)
    phase = np.arctan2(Hw.imag, Hw.real)
    
    if phaseShiftAsTime:
        # convert phase shift to time delay 
        #tmp = 1.0 / np.arange(1, numPoints)
        #tmp = np.append(0, tmp)
        tmp = np.zeros(numPoints)
        tmp[1:] = 1.0 / np.arange(1, numPoints)
        
        
        phase = phase / np.pi * 180
        phase[phase > 0] -= 180
        phase = -phase / 360.0 * tmp * 1000 #convert degree to milliseconds
    
    phase[0] = phase[1]
    return (magdB, phase)


def biquadEval(flt, samplingRate = 1000):
    b0, b1, b2, a1, a2 = flt.constants()
    zeros = [ b0, b1, b2 ]
    poles = [ 1.0, a1, a2 ]
    (magdB, phase) = filterEval(zeros, poles, samplingRate)
    
    return magdB, phase
