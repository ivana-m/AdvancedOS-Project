#!/usr/bin/python
#-*- coding: utf-8 -*-

def rect2canrects(rects):
    """Transforms list of rectangles to a canonical list of rectangles

    A canonical list of rectangles is a list of rectangles (see rectangle description below) such that for every
    pair of rectangles (i,j,k,x1,x2,y), (i',j',k',x1',x2',y'), we have:
    either (x1,x2) = (x1',x2') or the real intervals (x1,x2) and (x1',x2') are disjoint

    Arguments:
    rects: list of rectangles corresponding to tasks
    - each rectangle is a tuple (i,j,k,x1,x2,y)
    -- i: task number (obs. task number tasks is the idle task)
    -- j: machine number
    -- k: configuration number
    -- x1: initial time of rectangle (rectangle initial x)
    -- x2: final time of rectangle (rectangle final x)
    -- y: power usage (rectangle height)

    Returns:
    canrects: canonical list of rectangles corresponding to rects
    (i.e., some rectangles of rects will be splitted to make the list canonical)
    """

    timelist = set()

    for (i,j,k,x1,x2,y) in rects:
        timelist.add(x1)
        timelist.add(x2)

    timelist = list(timelist)
    timelist.sort() #this is to ensure that python didn't present us with the set out of order
    canrects = []
    for (i,j,k,x1,x2,y) in rects:
        t = timelist.index(x1)
        while timelist[t] != x2:
            canrects.append((i,j,k,timelist[t],timelist[t+1],y))
            t += 1
    return canrects

def drawrects(rects, drawrect, isCan=False, makecopy=False):
    """Draws rectangles from a list of rectangles (computing their y offsets) using drawrect

    Arguments:
    rects: list of rectangles corresponding to tasks
    - each rectangle is a tuple (i,j,k,x1,x2,y)
    -- i: task number (obs. task number tasks is the idle task)
    -- j: machine number
    -- k: configuration number
    -- x1: initial time of rectangle (rectangle initial x)
    -- x2: final time of rectangle (rectangle final x)
    -- y: power usage (rectangle height)
    drawrect: a function that receives i,j,k,x1,x2,y1,y2 and
    draws the rectangle [x1,x2] X [y1,y2] corresponding to task i in machine j with configuration k
    (obs.: i,j,k may be used by drawrect for colouring and/or labelling)
    isCan: True if rectangle list is known to be canonical (see documentation for rect2canrects). Default: False
    makecopy: boolean, if True, algorithm does not change any of its parameters (see Data races)

    Data races: 
    If makecopy = False, then
    - rects is modified
    """

    if not isCan:
        rects = rect2canrects(rects)
    elif makecopy:
        rects = rects[:]

    def key(rect):#Key to order rects
        (i,j,k,x1,x2,y) = rect
        return (x1,j) #Order rects by time, then machine

    rects.sort(key=key)

    lastTime = rects[0][3] #Initial time (x1)
    totalUsageNow = 0
    for (i,j,k,x1,x2,y) in rects:
        if lastTime < x1:
            lastTime = x1
            totalUsageNow = 0
        drawrect(i,j,k,x1,x2,totalUsageNow, totalUsageNow+y)
        totalUsageNow += y
