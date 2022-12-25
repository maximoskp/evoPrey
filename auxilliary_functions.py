#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 07:32:10 2022

@author: max
"""

import numpy as np

def limit_xy(x, y, m):
    v = np.sqrt( x**2 + y**2 )
    if v != 0:
        n = min(v,m)/v
    else:
        n = 0
    return n*x , n*y
# end limit_xy

def dist_2d_arrays( x , y ):
    return np.sqrt( (x[0]-y[0])**2 + (x[1]-y[1])**2 )
# end dist_2d_arrays

def cos_dist( x , y ):
    if np.linalg.norm(x) == 0 or np.linalg.norm(y) == 0:
        return 0
    return np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y))
# end cos_dist