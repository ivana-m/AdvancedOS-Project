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

def less2key(less, cls):
    class cls_less(cls):
        def __lt__(self, other):
            return less(cls(self), cls(other))
        def __gt__(self, other):
            return less(cls(other), cls(self))
        def __le__(self, other):
            return not less(cls(other), cls(self))
        def __ge__(self, other):
            return not less(cls(self), cls(other))
    return cls_less

class no_solution(BaseException): pass
