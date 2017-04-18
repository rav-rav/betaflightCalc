'''
Created on 20.03.2017

@author: rav
'''

import numpy as np

#betaflight pt1 for reference
class pt1Filt():
    RC = 0
    dT = 0
    k = 0
    state = 0
    
def pt1FilterInit(filter, f_cut, dT):
    filter.RC = 1.0 / ( 2.0 * np.pi * f_cut );
    filter.dT = dT;
    filter.k = filter.dT / (filter.RC + filter.dT);

def pt1FilterApply(filter, input):
    filter.state = filter.state + filter.k * (input - filter.state);
    return filter.state;

