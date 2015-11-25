#!/usr/bin/python
#-*- coding: utf-8 -*-

from commonclasses import stateTran

def val2file(filename, pwrusg, idle, idleusg, pwrcap, order, trn, run,
             begin='', sep='\t', end = '\n', hbegin='', hsep='\t', hend='\n', tail=''):
    """Writes file with all information for plotting

    Arguments:
    filename: output file name
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
    begin: string placed at the beginning of each logical line
    sep: separator string (placed between entries)
    end: string placed at end of each logical line
    hbegin: string placed at the beginning of the header
    hsep: header separator string (placed between entries of the header)
    hend: string placed at end of header
    tail: string placed at end of file

    Assumptions:
    trn non-empty
    there is a dummy transition at the end of trn (on the time of last completion)

    File format:
    Header:
    HB <#Tasks> HS <#Machines> HS <#Configurations> HS <pwrcap> HS <minimum time> HS <maximum time> HE
    where HB is hbegin, HS is hsep, and HE is hend.

    The file is composed of logical lines and each logical line is of the form:
    B <Task> S <Machine> S <Configuration> S <time1> S <time2> S <power usage> E
    where time1 <= time2, B is begin, S is sep, and E is end.

    Tasks are enumerated from 0 to #Tasks-1.
    When a machine idles, we represent it as an idle task running on it.
    The number of the idle task is represented as #Tasks.

    The file then ends with the tail string.
    """

    tasks = len(pwrusg)
    machines = len(pwrusg[0])
    configs = len(pwrusg[0][0])

    mintime = trn[0].time
    maxtime = mintime
    for t in trn:
        if t.time > maxtime:
            maxtime = t.time

    with open(filename, 'w') as f:
        f.write(hbegin + str(tasks) + hsep + str(machines) + hsep + str(configs) + hsep + str(pwrcap)
                + hsep + str(mintime) + hsep + str(maxtime) + hend)
        orderinds = [0] * machines
        for t in range(1,len(trn)):
            for j in range(machines):
                prevtime = trn[t-1].time #must be here
                k = trn[t-1].config[j]
                if orderinds[j] < len(order[j]):
                    while run[j][orderinds[j]+1] < trn[t].time:
                        #Tasks that finish before next transition
                        i = order[j][orderinds[j]]
                        f.write(begin + str(i) + sep + str(j) + sep + str(k) + sep
                                + str(prevtime) + sep + str(run[j][orderinds[j]+1])+ sep
                                + str(pwrusg[i][j][k]) + end)
                        orderinds[j] += 1
                        if orderinds[j] == len(order[j]):
                            break
                        prevtime = run[j][orderinds[j]]
                    if orderinds[j] < len(order[j]): #needed!
                        #Task that run up to transition time
                        i = order[j][orderinds[j]]
                        f.write(begin + str(i) + sep + str(j) + sep + str(k) + sep
                                + str(prevtime) + sep + str(trn[t].time) + sep
                                + str(pwrusg[i][j][k]) + end)
                        if run[j][orderinds[j]+1] == trn[t].time: #task finished on transition time
                            orderinds[j] += 1
                        prevtime = trn[t].time
                if orderinds[j] == len(order[j]): #needed!
                    #Nothing left to run
                    if prevtime < trn[t].time:
                        # But there is still time left: run idle task
                        f.write(begin + str(tasks) + sep + str(j) + sep + str(idle[j]) + sep
                                + str(prevtime) + sep + str(trn[t].time) + sep
                                + str(idleusg[j]) + end)
        #out of for
        f.write(tail)
        f.close()

def file2rects(filename, sep='\t', hsep='\t'):
    """Reads a file with all information for plotting

    Arguments:
    filename: input file name
    sep: separator string (placed between entries)
    hsep: header separator string (placed between entries of the header)

    Returns: A tuple (tasks, machines, configs, pwrcap, mintime, maxtime, rects)
    tasks: number of tasks
    machines: number of machines
    configs: number of configurations
    pwrcap: power cap
    mintime: minimum time
    maxtime: maximum time
    rects: list of rectangles corresponding to tasks
    - each rectangle is a tuple (i,j,k,x1,x2,y)
    -- i: task number (obs. task number tasks is the idle task)
    -- j: machine number
    -- k: configuration number
    -- x1: initial time of rectangle (rectangle initial x)
    -- x2: final time of rectangle (rectangle final x)
    -- y: power usage (rectangle height)

    Assumptions: file properly formatted (see format on val2file documentation) with only whitespaces
    in the strings begin, end, hbegin, hend, tail; and with separator sep and header separator hsep
    """

    with open(filename, 'r') as f:
        header = f.readline()
        (tasks, machines, configs, pwrcap, mintime, maxtime) = header.strip().split(hsep)
        tasks = int(tasks)
        machines = int(machines)
        configs = int(configs)
        pwrcap = float(pwrcap)
        mintime = float(mintime)
        maxtime = float(maxtime)

        rects = []
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            (i,j,k,x1,x2,y) = line.split(sep)
            i = int(i)
            j = int(j)
            k = int(k)
            x1 = float(x1)
            x2 = float(x2)
            y = float(y)

            rects.append((i,j,k,x1,x2,y))
        return (tasks, machines, configs, pwrcap, mintime, maxtime, rects)
