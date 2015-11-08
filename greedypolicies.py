#!/usr/bin/python
#-*- coding: utf-8 -*-

#These are the (probably) stupid ones:
def fast(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    return spd[i1][j1][k1] > spd[i1][j1][k1]

def short(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    return wrkld[i1][j1][k1] < wrkld[i1][j1][k1]

def economic(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    return pwrusg[i1][j1][k1] < pwrusg[i1][j1][k1]

#These are the 'somewhat make sense' ones:
def earlycompletion(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    # should be 
    # return wrkld[i1][j1][k1] / spd[i1][j1][k1] < wrkld[i2][j2][k2] / spd[i2][j2][k2]
    # but we make it like this to avoid zero division
    return wrkld[i1][j1][k1] * spd[i2][j2][k2] < wrkld[i2][j2][k2] * spd[i1][j1][k1]


def fastNeconomic(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    # should be
    # return pwrusg[i1][j1][k1] / spd[i1][j1][k1] < pwrusg[i2][j2][k2] / spd[i2][j2][k2]
    # but we make it like this to avoid zero division
    return pwrusg[i1][j1][k1] / spd[i1][j1][k1] < pwrusg[i2][j2][k2] / spd[i2][j2][k2]

def shortNeconomic(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    return wrkld[i1][j1][k1] * pwrusg[i1][j1][k1] < wrkld[i2][j2][k2] * pwrusg[i2][j2][k2]

#These are the ones that are not blind to any parameter
def leasttotalusage(wrkld, spd, pwrusg, (i1,j1,k1), (i2,j2,k2)):
    # should be
    # return wrkld[i1][j1][k1] * pwrusg[i1][j1][k1] / spd[i1][j1][k1] < wrkld[i2][j2][k2] * pwrusg[i2][j2][k2] / spd[i2][j2][k2]
    # but we make it like this to avoid zero division
    return wrkld[i1][j1][k1] * pwrusg[i1][j1][k1] * spd[i2][j2][k2] < wrkld[i2][j2][k2] * pwrusg[i2][j2][k2] * spd[i1][j1][k1]
