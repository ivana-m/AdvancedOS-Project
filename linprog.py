#!/usr/bin/python
#-*- coding: utf-8 -*-

import numpy
import scipy.optimize
import itertools
import commonclasses

class iteration_limit(BaseException): pass
class unboundedLP(BaseException): pass

def linearProgram(wrkld, spd, pwrusg, idle, idleusg, pwrcap, makecopy=True, epsilon=1e-9):
    """Schedules according to linear program

    Arguments:
    wrkld: list of workloads of each task
    spd: list of speeds of configurations states
    - for every task i, every machine j, and every configuration k,
    - spd[i][j][k] is the speed of task i in machine j while in configuration k
    pwrusg: list of power usages of configuration states
    - for every task i, every machine j, and every configuration k,
    - pwrusg[i][j][k] is the power usage of task i in machine j while in configuration k
    idle: list of idle configuration states
    - for every machine j
    - idle[j] is the idle configuration of machine j (i.e., the state with less power usage)
    idleusg: list of power usages of idle configuration states
    - for every machine j
    - idleusg[j] is the power usage of the idle configuration of machine j when no task is running
    pwrcap: power limit of the system
    makecopy: boolean, if True, algorithm does not change any of its parameters (see Data races)
    epsilon: precision for zero comparison


    Returns: A triple (order, trn, run)
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
    run: list of completion times of tasks
    - for every machine j, and every t in len(order[j])
    - task order[j] runs on machine j from time run[j][t] to time run[j][t+1]

    Exceptions raised:
    - no_solution if pwrcap cannot be satisfied

    Assumptions:
    Compatibility of sizes
    Non-negative values
    Non-zero tasks, machines and configurations
    Non-zero workloads
    Idle state usages are less than when tasks are being run
    Every task i on idle state idle[j] has same usage pwrusg[i][j][idle[j]] as idleusg[j]
    Every task on an idle state has speed zero

    Data races: 
    If makecopy = False, then
    - wrkld is modified
    """

    tasks = len(spd)
    machines = len(spd[0])
    nconfigs = len(spd[0][1])

    if makecopy:
        wrkld = wrkld[:]

    order = [None] * machines
    run = [None] * machines
    trn = []
    for j in range(machines):
        order[j] = []
        run[j] = [0]

    initialtime = 0
    thisalloc = [i for i in range(tasks) if i < machines] + [None] * (machines - tasks)
    nexttask = machines

    while True:
        # (order of the) variables of the linear program:
        # nconfigs ** machines variables (p_{sysconf}), one for each system configuration sysconf
        # objective variable (y): inverse of the maximum time (maxtime) of completion (y will be maximized)

        nsysconfigs = nconfigs ** machines
        objective = [0] * nsysconfigs + [-1]

        #Restrictions of the form a.x <= b
        upperboundedrestr = [] #list of a's
        upperboundedrhs = [] #list of b's

        #Restriction: each allocated task must have its workload completed:
        # The restriction is:
        # \sum_{sysconf} p_{sysconf} spd_{sysconf} * maxtime >= wrkld[task]
        # But we use (since y = 1 / maxtime):
        # - \sum_{sysconf} p_{sysconf} spd_{sysconf} + wrkld[task] * y <= 0
        for j in range(machines):
            if thisalloc[j] != None: #machine has an allocated task
                upperboundedrestr.append([-spd[thisalloc[j]][j][sysconf[j]]
                                          for sysconf in itertools.product(range(nconfigs), repeat=machines)]
                                         + [wrkld[thisalloc[j]]])#y
                upperboundedrhs.append(0)#right-hand side

        #Restriction: coefficients of system configuration sum to 1
        equalityrestrs = [[1] * nsysconfigs
                         + [0]]#y
        equalityrhs = [1]#right-hand side

        bounds = [None] * (nsysconfigs + 1)
        for var in range(nsysconfigs + 1):
            bounds[var] = (0,None)#all variables are non-negative

        #Restriction): every sysconf that consumes more than powercap cannot be used:
        #p_{sysconf} = 0 for every sysconf with \sum_j pwrusg[task][machine][sysconf[j]] > pwrcap
        #put as the sum of such p_{sysconf} equals 0
        restr = [0] * (nsysconfigs + 1)
        for index,sysconf in enumerate(itertools.product(range(nconfigs), repeat=machines)):
            thispwrusg = 0
            for j in range(machines):
                if thisalloc[j] != None: #machine has an allocated task
                    thispwrusg += pwrusg[thisalloc[j]][j][sysconf[j]]
                elif sysconf[j] == idle[j]: #machine does not have allocated task: it should idle
                    thispwrusg += idleusg[j]
                else: #machine does not have allocated task but is not idle: forbid system configuration
                    thispwrusg += pwrcap + 1
                    break
            if thispwrusg > pwrcap:
                restr[index] = 1#force coefficient to be zero
        equalityrestrs.append(restr)
        equalityrhs.append(0)
        
        #Solve linear program
        LPresult = scipy.optimize.linprog(c=objective,
                                          A_ub=upperboundedrestr,
                                          b_ub=upperboundedrhs,
                                          A_eq=equalityrestrs,
                                          b_eq=equalityrhs)

        if LPresult.nit == 1:
            raise iteration_limit
        if LPresult.nit == 2:
            raise commonclasses.no_solution
        if LPresult.nit == 3:
            raise unboundedLP #This should never be raised if the workloads are non-zero

        #Compute task effective speeds and completion times
        effectivespeeds = [None] * machines
        completiontimes = [None] * machines
        mincompletiontime = 2.0/LPresult.x[-1] #= 2/y = 2*maxtime (the 2 is to avoid precision errors)
        for j in range(machines):
            if thisalloc[j] != None: #machine had an allocated task
                effectivespeeds[j] = 0
                for index,sysconf in enumerate(itertools.product(range(nconfigs), repeat=machines)):
                    effectivespeeds[j] += LPresult.x[index] * spd[thisalloc[j]][j][sysconf[j]]
                completiontimes[j] = float(wrkld[thisalloc[j]]) / effectivespeeds[j]
                if mincompletiontime > completiontimes[j]:
                    mincompletiontime = completiontimes[j]

        finished = True #boolean that will indicate all tasks have been completed
        #Every task completed in time mincompletiontime is deemed completed
        #All other tasks will be rescheduled (with updated workloads)
        for j in range(machines):
            if thisalloc[j] != None:
                if completiontimes[j] <= mincompletiontime + epsilon:
                    order[j].append(thisalloc[j])
                    run[j].append(initialtime + completiontimes[j])
                    if nexttask < tasks:
                        finished = False
                        thisalloc[j] = nexttask
                        nexttask += 1
                    else:
                        thisalloc[j] = None
                else: #machine had an allocated task that took more than mincompletiontime
                    wrkld[thisalloc[j]] -= mincompletiontime * effectivespeeds[j]

        #Add transition at time initialtime to pseudo state given by LP solution
        p = numpy.empty([nconfigs]*machines) #empty array
        for index,sysconf in enumerate(itertools.product(range(nconfigs), repeat=machines)):
            p[sysconf] = LPresult.x[index]
        trn.append(commonclasses.pseudoStateTran(initialtime, p))

        if finished:
            for j in range(machines):
                if thisalloc[j] != None: #machine had an allocated task that took more than mincompletiontime
                    order[j].append(thisalloc[j])
                    run[j].append(initialtime + completiontimes[j])
                elif len(run[j]) == 1: #machine was never used, remove initial run time
                    run[j] = []
            #Add final transition to idle states
            p = numpy.full([nconfigs]*machines,0) #array filled with 0s
            p[tuple(idle)] = 1
            trn.append(commonclasses.pseudoStateTran(initialtime + 1.0/LPresult.x[-1], p))
            return (order,trn,run) #RETURN IS HERE!!!

        initialtime = mincompletiontime #go to time mincompletiontime
    #linearProgram's return is inside while True loop...

import translation

def realLinearProgram(wrkld, spd, pwrusg, idle, idleusg, pwrcap, makecopy=True):
    """Schedules according to linear program

    Acts as a wrapper to linearProgram and translates its return value using
    translation.getRealTransitionsFromPseudo

    For arguments, exceptions, assumptions and data races, see linearProgram.

    Returns: A triple (order, trn, run)
    order: list of orderings of tasks on machines
    - for every machine j,
    - order[j] is a list [i1, ..., ik] that describes the tasks that will be run on machine j and their order
    trn: list of state transitions
    - for every t in range(len(trn)),
    - trn[t].time is the time of transition t
    - trn[t].config is a list of machine configurations
    -- for every machine j,
    -- trn[t].config[j] is the configuration to which machine j has transitioned
    run: list of completion times of tasks
    - for every machine j, and every t in len(order[j])
    - task order[j] runs on machine j from time run[j][t] to time run[j][t+1]
    """

    (order, psdtrn, run) = linearProgram(wrkld, spd, pwrusg, idle, idleusg, pwrcap, makecopy)
    trn = translation.getRealTransitionsFromPseudo(psdtrn, run, idle)
    return (order, trn, run)
