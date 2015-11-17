#!/usr/bin/python
#-*- coding: utf-8 -*-

workload = [10] * 3
speed = [[[0, 1, 2, 3]] * 3] * 3
powerusage = [[[1, 2, 3, 4]] * 3] * 3
powercap = 7
idlestates = [0] * 3
idleusage = [1] * 3

import linprog; linprog.linear_program(
    workload, speed, powerusage, idlestates, idleusage, powercap)