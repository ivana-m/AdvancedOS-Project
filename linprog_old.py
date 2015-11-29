import numpy
import scipy.optimize

def linear_program(wrkld, spd, pwrusg, idle, idleusg, pwrcap):
    """Schedules tasks so that the last task finishes the soonest.

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
    plcy: function that receives wrkld, spd, pwrusg and two triples (i1,j1,k1) and (i2,j2,k2) and returns True
    if and only if (i1,j1,k1) < (i2,j2,k2) in the policy used to greedly allocate the task
    (i.e., triple (i1,j1,k1) is preferred over (i2,j2,k2))
    --> plcy may assume that it will receive triples that don't yield zero speed

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
    configurations = len(spd[0][1])

    if tasks != machines:
        raise ValueError("must have only one task per machine")

    equality = []
    inequality = []
    objective = []

    # Run only one instance on each task/machine.
    for task in xrange(tasks):
        one_per_machine = [0] * (configurations * tasks) + [0, 1]
        for configuration in xrange(configurations):
            one_per_machine[configuration + task * configurations] = int(
                pwrusg[task][task][configuration] <= pwrcap)
        equality.append(one_per_machine)

    # Filter out tasks that are infeasible (speed == 0, power >= cap)
    for task in xrange(tasks):
        for configuration in xrange(configurations):
            if (pwrusg[task][task][configuration] >= pwrcap or
                spd[task][task][configuration] == 0):

                only_feasible = [0] * (configurations * tasks) + [0, 0]
                only_feasible[configuration + task * configurations] = 1
                equality.append(only_feasible)

    # Ensure that the total energy is less than the threshold.
    power_less_than_cap = [0] * (configurations * tasks) + [0, pwrcap]
    index = 0
    for task in xrange(tasks):
        for configuration in xrange(configurations):
            power_less_than_cap[index] = pwrusg[task][task][configuration]
            index += 1
    inequality.append(power_less_than_cap)

    # Ensure that each task's completion time is less than the bound.
    index = 0
    for task in xrange(tasks):
        for configuration in xrange(configurations):
            time_less_than_slack = [0] * (configurations * tasks) + [-1, 0]
            units_per_second = spd[task][task][configuration]
            total_units = wrkld[task]
            if units_per_second > 0:
                time_less_than_slack[index] = float(total_units) / units_per_second
            inequality.append(time_less_than_slack)
            index += 1

    # Rewrite lists into matrices.
    c = [0] * (configurations * tasks) + [1]
    A_ub = [x[:-1] for x in inequality]
    b_ub = [x[-1] for x in inequality]
    A_eq = [x[:-1] for x in equality]
    b_eq = [x[-1] for x in equality]

    result = scipy.optimize.linprog(
        c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq)

    print result

    # ~ somehow turn result.x into a list of transitions ~
