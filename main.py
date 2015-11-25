import greedy
import greedypolicies
import fileio
import rectangles
import os

import matplotlib.pyplot as plt #use for drawing
import matplotlib.patches as patches #use for drawing

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

#policies = [greedypolicies.fast, greedypolicies.short, greedypolicies.economic, greedypolicies.earlycompletion, 
            
policies = [greedypolicies.fastNeconomic, greedypolicies.shortNeconomic, greedypolicies.leasttotalusage, greedypolicies.long, greedypolicies.makelongshort, greedypolicies.longNeconomic, greedypolicies.longNeconomicNfast]

#policiesList = ["fast", "short", "economic", "earlycompletion", 
                
policiesList = ["fastNeconomic", "shortNeconomic", "leasttotalusage", "long", "makelongshort", "longNeconomic", "longNeconomicNfast"]

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
                

#generate_files()



colors = ['r','g','b','y', 'c', 'm']
idleCol = '0.7'

#use this at the very beginning
def init_figure():
    plt.ioff()
    fig = plt.figure(figsize=(17,15),dpi=100) #values obtained by handtweaking, but might be subject to change. size works well for 26 applications at once. For a smaller image, just remove the arguments and use:
    #fig = plt.figure() #instead
    return fig

def add_rectangle(ax, x, y, w, h, col):
    ax.add_patch(
        patches.Rectangle(
            (x,y), w, h,
            edgecolor = 'none',
            facecolor = col
            )
        )
    
#if you want to save the output of the figure as an image, use this at the very end
def save_figure(fig, fileName):
    fig.savefig(fileName+'.png', dpi='figure', bbox_inches='tight') 
    plt.close() #close plot - prevents plot from displaying. Use if generating many plots at once
    
def add_label(ax, text, x, y, fontsize):
    ax.text(x,y,text,fontsize=fontsize)
          
def draw(f, fname, cols, idlecol):
    fig = init_figure()
    ax = fig.add_subplot(111)
    
    tasks, machines, configs, pwrcap, mintime, maxtime, rects = fileio.file2rects(f)    
    
    def drawTask(i, j, k, x1, x2, y1, y2):
        col = idlecol
        if(i < tasks):
            col = cols[i % len(cols)]
        add_rectangle(ax, x1, y1, (x2-x1), (y2-y1), col)
        
    rectangles.drawrects(rects, drawTask)
    ax.axhline(y = pwrcap, c = 'r', linewidth=1, zorder=5)
    plt.plot([maxtime,maxtime],[0,pwrcap], '0.75')
    save_figure(fig, fname)
    
    

def process_files(dir):
    for policy in policies:
        for numTasks in range(1, totalNumTasks + 1):
            for powerCap in range(1000, maxPowerCap, 400):
                fn = policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks)
                fname = os.path.join(dir, fn)
                
                f = open(fname, 'r')
                draw(f, fn, cols, idlecol)
                

#f = "output/greedy/fast-1000-7"
#draw(f, "fast-1000-7", colors, idleCol)



                
          
                
                
                
  
    
        
        

            
            
      
            
            
            

