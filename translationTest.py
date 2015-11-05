#!/usr/bin/python
#-*- coding: utf-8 -*-

from translation import stateTran
from translation import pseudoStateTran
from numpy import array

workload = [10] * 6
speed = [[[1, 2, 3]] * 3] * 6

order = [[0,1],
         [2,3],
         [4,5]]

realtransitions = [stateTran(0,[0,0,0]),
                   stateTran(2,[1,2,0]),
                   stateTran(5,[2,0,1]),
                   stateTran(7,[2,2,2]),
                   stateTran(10,[1,1,1])]
pseudotransitions = [
    pseudoStateTran(0,array([
        [[1,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]]])),
    pseudoStateTran(2,array([
        [[1/2,0,1/2],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]]])),
    pseudoStateTran(5,array([
        [[1/4,0,1/4],[0,0,0],[1/4,0,1/4]],
        [[0,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]]])),
    pseudoStateTran(11,array([
        [[0,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,0]],
        [[0,0,0],[0,0,0],[0,0,1]]]))
]
