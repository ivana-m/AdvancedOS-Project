import greedy
import greedypolicies
import fileio
import os

#class Task(object):
    #def __init__(self, index, configIndex, power, speed):
        #self.index = int(index)
        #self.configIndex = float(configIndex)
        #self.powerUsage = float(power)
        #self.speed = float(speed)
        
def load_tasks(n, m, dir, idlePow):
    taskSpeed = []
    speed = []
    taskPow = []
    pu = []
    for i in range(0,n):
        #if(i == 8): #the really slow filebound
            #continue
        taskFile = open(dir+"/"+str(i),'r')
        #taskRuns = []
        for line in taskFile:
            properties = line.strip().split('\t')
            #index = i
            #configIndex = properties[0]
            performance = properties[1]
            power = properties[2]
            taskSpeed.append(float(performance))
            taskPow.append(float(power))
            #time = properties[3]
            #tsk = Task(index, configIndex, power, time, performance)
            #taskRuns.append(tsk)
        #tasks.append(taskRuns)
        taskSpeed.append(0.0)
        taskPow.append(idlePow)
        speed.append([taskSpeed] * m)
        pu.append([taskPow] * m)
        taskSpeed = []
        taskPow = []
        taskFile.close()
    #print(len(speed), len(speed[0]), len(speed[0][0]))
    return speed, pu#tasks


appd = "applications"
greedyOut = "output/greedy"
smrtGreedyOut = "output/smartGreedy"

totalNumTasks = 27
numMachines = 5
maxPowerCap = 6600
idlePow = 90.0
totalWkld = 10
idlestates = [1024] * numMachines
idleusage = [idlePow] * numMachines

policies = [greedypolicies.fast, greedypolicies.short, greedypolicies.economic, greedypolicies.earlycompletion, greedypolicies.fastNeconomic, greedypolicies.shortNeconomic, greedypolicies.leasttotalusage]

policiesList = ["fast", "short", "economic", "earlycompletion", "fastNeconomic", "shortNeconomic", "leasttotalusage"]

def generate_files():
    for policy in policies:
        for numTasks in range(1, totalNumTasks + 1):
            speed, pu = load_tasks(numTasks, numMachines, appd, idlePow)
            workload = [totalWkld] * numTasks
            for powerCap in range(1000, maxPowerCap, 400):
                
                order, trn, run = greedy.greedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                out = os.path.join(greedyOut, policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks))
                #print(numTasks, powerCap,policiesList[policies.index(policy)])
                fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                #do the same for smart
                #orderS, trnS, runS = greedy.smartGreedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                #outS = os.path.join(smrtGreedyOut, policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks))
                #fileio.val2file(outS, pu, idlestates, idleusage, powerCap, orderS, trnS, runS)
                

generate_files()
          
def process_files():
    for policy in policies:
        for numTasks in range(1, totalNumTasks + 1):
            for powerCap in range(1000, maxPowerCap, 400):
                fname = os.path.join(greedyOut, policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks))
                
                f = open(fname, 'r')
                
                fileio.file2rects(f)
                
  
    
        
        

            
            
      
            
            
            

