#!/usr/bin/python
#-*- coding: utf-8 -*-

class no_solution: pass

import heapq

def greedy(wrkld, spd, pwrusg, idle, idleusg, pwrcap, plcy):
    """Greedly schedules tasks according to a certain policy (no transitions while executing a task)

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
    plcy: function that receives wkld, spd, pwrusg and two triples (i1,j1,k1) and (i2,j2,k2) and returns True
    if and only if (i1,j1,k1) < (i2,j2,k2) in the policy used to greedly allocate the task
    (i.e., triple (i1,j1,k1) is preferred over (i2,j2,k2))

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

    Exceptions raised:
    - no_solution if pwrcap cannot be satisfied

    Assumptions:
    Compatibility of sizes
    Non-negative values
    Non-zero tasks, machines and configurations
    Idle state usages are less than when tasks are being run
    Every task i on idle state idle[j] has same usage pwrusg[i][j][idle[j]] as idleusg[j]
    Every task on an idle state has speed zero
    """

    tasks = len(spd)
    machines = len(spd[0])
    configs = len(spd[0][0])

    order = [None] * machines
    trn = []
    run = [None] * machines

    for j in range(machines):
        order[j] = []
        run[j] = [0]

    possib = [(i,j,k)
              for i in range(tasks)
              for j in range(machines)
              for k in range(configs)
              if pwrusg[i][j][k] <= pwrcap and spd[i][j][k] > 0 #exclude violating configs and zero speeds
          ].sort(key=lambda t1,t2: plcy(wkld,spd,pwrusg,t1,t2))
    
    taskcompleted = [False] * tasks
    events = [(0, #time
               0)#machine that became free (first value is irrelevant)
           )]
    currentconfigs = [idle[j] for j in range(machines)]
    currentpwrusgs = [idleusg[j] for j in range(machines)]
    currenttotalpwrusg = sum(currentpwrusgs)
    currentfree = [True] * machines
    numberoffree = machines
    
    while True: #Equivalent to while len(events) != 0 here
        (time, becamefree) heapq.heappop(events)
        # currentfree update block
        while True:
            if not free[becamefree]:
                free[becamefree] = True
                numberoffree += 1
                currenttotalpwrusg += currentpwrusg[becamefree] - idleusg[becamefree]
                currentpwrusg[becamefree] = idleusg[becamefree]
                currentconfigs[becamefree] = idle[becamefree]
            if len(events) == 0 or events[0][0] != time:
                break
            #next event has the same time (i.e., more machines may have become free at time)
            becamefree = heapq.heappop(events)[1]
        # End currentfree update block

        psbind = 0 #since deletion in list possib is involved, we must do it like this
        while numberoffree:
            while psbind < len(possib):
                i,j,k = possib[psbind]
                if taskcompleted[i] = True: # task is completed: can be removed from possibilities
                    del possib[psbind]
                    continue # avoid incrementing index psbind
                if currentfree[j] and currenttotalpwrusg - currentpwrusgs[j] + pwrusg[i][j][k] <= pwrcap:
                    break # found best valid triple!
                psbind += 1
            else: # (while's else) cannot run any more tasks at this time
                if numberoffree == machines: #no occupied machine: either we are done or there is no solution
                    if False in taskcompleted: #some task is left: no solution
                        raise no_solution
                    for j in range(machines):# Fix run for machines that never ran any task
                        if len(order) == 0:
                            run[j] = []
                    trn.append(stateTran(time,currentconfigs))#add final transition to idle states at the end
                    return (order,trn,run) #RETURN IS HERE!!

            # Run i on j with config k block
            taskcompleted[i] = True
            del possib[psbind]
            order[j].append(i)
            currenttotalpwrusg += pwrusg[i][j][k] - currentusgs[j] 
            currentconfigs[j] = k
            currentpwrusgs[j] = pwrusg[i][j][k]
            #transition left to be updated after all tasks of this time are processed

            completiontime = time + wrkld[i] / spd[i][j][k] #speed guaranteed to be non-zero
            run[j].append(completiontime)
            heapq.heappush((completiontime,j)) #machine j will become free at time completiontime

            currentfree[j] = False
            numberoffree -= 1
            # End of run i on j with config k block

        #update transition of this time
        trn.append(stateTran(time,currentconfigs))
    #greedy's return is inside while True loop...
