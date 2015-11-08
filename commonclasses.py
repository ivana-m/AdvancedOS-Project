#!/usr/bin/python
#-*- coding: utf-8 -*-

class stateTran:
    def __init__(self,_time,_config):
        self.time = _time
        self.config = _config
    def __str__(self):
        return str((self.time,self.config))

class pseudoStateTran:
    def __init__(self,_time,_configcoeff):
        self.time = _time
        self.configcoeff = _configcoeff
    def __str__(self):
        return str((self.time,self.configcoeff))
