#!/usr/bin/python
#-*- coding: utf-8 -*-

from commonclasses import stateTran, pseudoStateTran

def getAssignmentCompletionFromReal(wrkld, spd, order, trn):
    """Computes the assignment/completion times from a solution given by order plus transitions into real
    system states (does not check for correctness of the solution)

    Arguments:
    wrkld: list of workloads of each task
    spd: list of speeds of configurations states
    - for every task i, every machine j, and every configuration k,
    - spd[i][j][k] is the speed of task i in machine j while in configuration k
    order: list of orderings of tasks on machines
    - for every machine j,
    - order[j] is a list [i1, ..., ik] that describes the tasks that will be run on machine j and their order
    trn: list of state transitions
    - for every t in range(len(trn)),
    - trn[t].time is the time of transition t
    - trn[t].config is a list of machine configurations
    -- for every machine j,
    -- trn[t].config[j] is the configuration to which machine j has transitioned

    Returns:
    A list run such that
    - for every machine j, and every t in len(order[j])
    - task order[j][t] runs on machine j from time run[j][t] to time run[j][t+1]

    Assumptions:
    trn has at least one element
    Times in trn are non-decreasing
    """

    machines = len(order) # number of machines
    run = [None] * machines
    time = trn[0].time

    runningindex = [None] * machines
    wrkldleft = [None] * machines
    for j in range(machines):
        if order[j]:
            run[j] = [time]
            runningindex[j] = 0
            wrkldleft[j] = wrkld[order[j][runningindex[j]]]

    for t in range(1,len(trn)):
        newtime = trn[t].time
        for j in range(machines):
            timeleft = newtime - time #this must be put here, and not outside
            while runningindex[j] != None:
                speed = spd[order[j][runningindex[j]]][j][trn[t-1].config[j]]
                processed = speed * timeleft
                if processed < wrkldleft[j]:
                    wrkldleft[j] -= processed
                    break
                timeleft -= wrkldleft[j]/speed
                run[j].append(newtime-timeleft)
                runningindex[j] += 1
                if len(order[j]) > runningindex[j]:
                    wrkldleft[j] = wrkld[order[j][runningindex[j]]]
                else:
                    runningindex[j] = wrkldleft[j] = None
        time = newtime

    #After last configuration transition
    for j in range(machines):
        lasttime = time #this must be put here, and not outside
        while runningindex[j] != None:
            speed = spd[order[j][runningindex[j]]][j][trn[-1].config[j]]
            lasttime += wrkldleft[j]/speed
            run[j].append(lasttime)
            runningindex[j] += 1
            if len(order[j]) > runningindex[j]:
                wrkldleft[j] = wrkld[order[j][runningindex[j]]]
            else:
                runningindex[j] = wrkldleft[j] = None
    return run

#----------------------------------------------------------------------------------------------------

import itertools

def getAssignmentCompletionFromPseudo(wrkld, spd, order, trn):
    """Computes the assignment/completion times from a solution given by order plus transitions into pseudo
    system states (does not check for correctness of the solution)

    Arguments:
    wrkld: list of workloads of each task
    spd: list of speeds of configurations states
    - for every task i, every machine j, and every configuration k,
    - spd[i][j][l] is the speed of task i in machine j while in configuration k
    order: list of orderings of tasks on machines
    - for every machine j,
    - order[j] is a list [i1, ..., ik] that describes the tasks that will be run on machine j and their order
    trn: list of state transitions
    - for every t in range(len(trn)),
    - trn[t].time is the time of transition t
    - trn[t].configcoeff is an numpy.array of machine configurations
    -- for every system configuration (l1,...,lm), where m is the number of machines,
    -- trn[t].configcoeff[l1,...,lm] is the coefficient of real system configuration (l1,...,lm) in the
       pseudo system configuration to which machine j has transitioned

    Returns:
    A list run such that
    - for every machine j, and every t in len(order[j])
    - task order[j][t] runs on machine j from time run[j][t] to time run[j][t+1]

    Assumptions:
    trn has at least one element
    all machines have the same number of configurations
    Times in trn are non-decreasing
    """

    machines = len(order) # number of machines
    run = [None] * machines
    time = trn[0].time
    nconfigs = len(trn[0].configcoeff) # number of configurations

    runningindex = [None] * machines
    wrkldleft = [None] * machines
    for j in range(machines):
        if order[j]:
            run[j] = [time]
            runningindex[j] = 0
            wrkldleft[j] = wrkld[order[j][runningindex[j]]]

    for t in range(1,len(trn)):
        newtime = trn[t].time
        psdnow = [(trn[t-1].configcoeff[sysconf], list(sysconf))
                  for sysconf in itertools.product(range(nconfigs), repeat=machines)# iterator for system configs
                  if trn[t-1].configcoeff[sysconf] != 0]
        for j in range(machines):
            timeleft = newtime - time #this must be put here, and not outside
            while runningindex[j] != None:
                speed = 0
                for (p,sysconf) in psdnow:
                    speed += p * spd[order[j][runningindex[j]]][j][sysconf[j]]
                processed = speed * timeleft
                if processed < wrkldleft[j]:
                    wrkldleft[j] -= processed
                    break
                timeleft -= wrkldleft[j]/speed
                run[j].append(newtime-timeleft)
                runningindex[j] += 1
                if len(order[j]) > runningindex[j]:
                    wrkldleft[j] = wrkld[order[j][runningindex[j]]]
                else:
                    runningindex[j] = wrkldleft[j] = None
        time = newtime

    #After last configuration transition
    psdnow = [(trn[-1].configcoeff[sysconf], list(sysconf))
              for sysconf in itertools.product(range(nconfigs), repeat=machines)# iterator for system configs
              if trn[-1].configcoeff[sysconf] != 0]
    for j in range(machines):
        lasttime = time #this must be put here, and not outside
        while runningindex[j] != None:
            speed = 0
            for (p,sysconf) in psdnow:
                speed += p * spd[order[j][runningindex[j]]][j][sysconf[j]]
            lasttime += wrkldleft[j]/speed
            run[j].append(lasttime)
            runningindex[j] += 1
            if len(order[j]) > runningindex[j]:
                wrkldleft[j] = wrkld[order[j][runningindex[j]]]
            else:
                runningindex[j] = wrkldleft[j] = None
    return run

#----------------------------------------------------------------------------------------------------

def getAssignmentCompletionRealTransitionsFromPseudo(wrkld, spd, order, trn, run=None, finaltrnconfig=None):
    """Computes the assignment/completion times from a solution given by order plus transitions into pseudo
    system states (does not check for correctness of the solution)

    Arguments:
    wrkld: list of workloads of each task
    spd: list of speeds of configurations states
    - for every task i, every machine j, and every configuration k,
    - spd[i][j][l] is the speed of task i in machine j while in configuration k
    order: list of orderings of tasks on machines
    - for every machine j,
    - order[j] is a list [i1, ..., ik] that describes the tasks that will be run on machine j and their order
    trn: list of state transitions
    - for every t in range(len(trn)),
    - trn[t].time is the time of transition t
    - trn[t].configcoeff is an numpy.array of machine configurations
    -- for every system configuration (k1,...,km), where m is the number of machines,
    -- trn[t].configcoeff[k1,...,km] is the coefficient of real system configuration (k1,...,km) in the
       pseudo system configuration to which machine j has transitioned
    run: describes when each task runs on each machine (or None (default) to let the function compute this)
    -- for every machine j, and every t in len(order[j])
    -- task order[j][t] runs on machine j from time run[j][t] to time run[j][t+1]

    finaltrnconfig: list of machine configurations to be put at the end
    (or None (default), which is equivalent to [0]*machines)
    --- for every machine j,
    --- finaltrnconfig[j] is the configuration to which machine j has transitioned
    (this is typically the list of idle configurations)

    Returns:
    A tuple (run,realtrn), where
    - run: describes when each task runs on each machine
    -- for every machine j, and every t in len(order[j])
    -- task order[j][t] runs on machine j from time run[j][t] to time run[j][t+1]
    - realtrn: is the list of real state transitions
    -- for every t in range(len(realtrn)),
    -- realtrn[t].time is the time of transition t
    -- realtrn[t].config is a list of machine configurations
    --- for every machine j,
    --- realtrn[t].config[j] is the configuration to which machine j has transitioned

    Assumptions:
    If run==None, then assumptions of getAssignmentCompletionFromPseudo
    """
    if run == None:
        run = getAssignmentCompletionFromPseudo(wrkld,spd,order,trn)
    if finaltrnconfig == None:
        finaltrnconfig = [0]*machines
    events = []
    realtrn = []
    machines = len(run)
    nconfigs = len(trn[0].configcoeff) # number of configurations

    for j in range(machines):
        if run[j]:
            for t in range(1,len(run[j])):
                events.append((run[j][t],j,t))

    for t in range(1,len(trn)):
        events.append((trn[t].time,machines,t)) # we put the transitions with a dummy marker on second coordinate

    events.sort()
    lasttime = trn[0].time
    psdnow = [(trn[0].configcoeff[sysconf], list(sysconf))
              for sysconf in itertools.product(range(nconfigs), repeat=machines)# iterator for system configurations
              if trn[0].configcoeff[sysconf] != 0] # first pseudo system state

    for (time,j,t) in events:
        if lasttime < time:
            difftime = time - lasttime
            splittime = lasttime
            for (p,sysconf) in psdnow:
                realtrn.append(stateTran(splittime,sysconf))
                splittime += p * difftime
            lasttime = time
        if j == machines: # it is a pseudo system state transition
            psdnow = [(trn[t].configcoeff[sysconf], list(sysconf))
                      for sysconf in itertools.product(range(nconfigs), repeat=machines)# iterator for system configurations
                      if trn[t].configcoeff[sysconf] != 0]
    #The part below normalizes the solution by putting a final state transition at the end
    realtrn.append(stateTran(lasttime,finaltrnconfig))
    return (run,realtrn)
