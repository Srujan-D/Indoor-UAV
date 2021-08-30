#!/usr/bin/env python

import numpy as np

class Node():    
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.parent = None
