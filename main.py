import greedy
import linprog
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


              
hfgreedy1 = [greedypolicies.economic, greedypolicies.leasttotalusage, greedypolicies.fast] 
hfgreedy2 = [greedypolicies.economic, greedypolicies.fast]

hfgreedy3 = [greedypolicies.economic, greedypolicies.leasttotalusage, greedypolicies.earlycompletion] 
hfgreedy4 = [greedypolicies.economic, greedypolicies.earlycompletion]

hf = [hfgreedy1, hfgreedy2, hfgreedy3, hfgreedy4]


def create_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)    

def generate_files(master, dirN):
    
    for numTasks in range(1, totalNumTasks + 1):
        speed, pu = load_tasks(numTasks, numMachines, appd, idlePow)
        workload = [totalWkld] * numTasks
        for powerCap in range(1000, maxPowerCap, 400):
            try:
                newPath = os.path.join(master,dirN)
                #create_dir(newPath)
                #out = newPath+"-"+str(powerCap)+"-"+str(numTasks))
                
                if(dirN == "greedy"):
                    for policy in policies:
                        newPath = os.path.join(newPath, policiesList[policies.index(policy)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+str(numTasks)                    
                        order, trn, run = greedy.greedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                elif(dirN == "smartGreedy"):
                    for policy in policies:
                        newPath = os.path.join(newPath, policiesList[policies.index(policy)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+str(numTasks)                     
                        order, trn, run = greedy.smartGreedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                    
                elif(dirN == "halfHeartedGreedy"):
                    for policy in policies:
                        newPath = os.path.join(newPath, policiesList[policies.index(policy)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+str(numTasks)                     
                        order, trn, run = greedy.smartGreedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run) 
                    
                elif(dirN == "lingProg"):
                    out = newPath+"-"+str(powerCap)+"-"+str(numTasks) 
                    order, trn, run = linprog.realLinearProgram(workload, speed, pu, idlestates, idleusage, powerCap)
                    fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                    
                #elif(dirN == "naive"):
                    #TODO
                    
                #elif(dirN == "not-so-naive"):
            except:
                pass
        
            

#generate_files()



colors = ['#FF0000','#0000FF','#006400','#FFD700','#B22222','#4B0082','#008000','#FFA500','#800000','#008B8B','#808000','#DAA520','#FF00FF','#00FFFF','#00FF00','#D2691E','#FF1493','#008080','#556B2F','#D8BFD8','#8B4513','#000080','#00FF7F','#BDB76B','#CD5C5C','#1E90FF','#FF7F50']

idleCol = '0.5'

#use this at the very beginning
def init_figure():
    plt.ioff()
    fig = plt.figure(figsize=(17,15),dpi=160) #values obtained by handtweaking, but might be subject to change. size works well for 26 applications at once. For a smaller image, just remove the arguments and use:
    #fig = plt.figure() #instead
    return fig

def add_rectangle(ax, x, y, w, h, col):
    ax.add_patch(
        patches.Rectangle(
            (x,y), w, h,
            edgecolor = 'none',
            facecolor = col,
            #hatch='x'
            )
        )
    
def add_idle_rectangle(ax, x, y, w, h, col):
    ax.add_patch(
        patches.Rectangle(
            (x,y), w, h,
            edgecolor = col,
            linewidth=0,
            #facecolor = col,
            hatch='xx',
            fill=False
            )
        )    
    
#if you want to save the output of the figure as an image, use this at the very end
def save_figure(fig, fileName):
    fig.savefig(fileName+'.png', dpi='figure', bbox_inches='tight') 
    plt.close() #close plot - prevents plot from displaying. Use if generating many plots at once
    
def add_label(ax, text, x, y, fontsize):
    ax.text(x,y,text,fontsize=fontsize)
          
def draw(fname, cols, idlecol):
    fig = init_figure()
    ax = fig.add_subplot(111)
    
    tasks, machines, configs, pwrcap, mintime, maxtime, rects = fileio.file2rects(fname)    
    
    def drawTask(i, j, k, x1, x2, y1, y2):
        
        if(i < tasks):
            col = cols[i % len(cols)]
            add_rectangle(ax, x1, y1, (x2-x1), (y2-y1), col)
        else:
            add_idle_rectangle(ax, x1, y1, (x2-x1), (y2-y1), idlecol)
        
    rectangles.drawrects(rects, drawTask)
    ax.axhline(y = pwrcap, c = 'r', linewidth=1, zorder=5)
    plt.plot([maxtime,maxtime],[0,pwrcap], '0.75')
    plt.ylabel("Power")
    plt.xlabel("Time")
    plt.title(fname.split('-')[0]+" policy, power cap: "+fname.split('-')[1]+", #tasks: "+fname.split('-')[2], fontsize = 14)
    save_figure(fig, fname)
    
    

def stats_info(fname):
    tasks, machines, configs, pwrcap, mintime, maxtime, rects = fileio.file2rects(fname)
    sumarea = idlearea = 0
    def addAreas(i, j, k, x1, x2, y1, y2):
        sumarea += (x2-x1) * (y2 - y1)
        if(i == tasks):
            idlearea += (x2-x1) * (y2 - y1)
            
    rectangles.drawrects(rects, addAreas)
    
    totalarea = ((maxtime-mintime) * pwrcap)
    wasted = totalarea - sumarea
    
    return maxtime, totalarea, sumarea, wasted, idlearea
    
    


def draw_files(dir):
    for policy in policies:
        for numTasks in range(1, totalNumTasks + 1):
            for powerCap in range(1000, maxPowerCap, 400):
                try:
                    fn = policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks)
                    fname = os.path.join(dir, fn)
                    
                    draw(fn, cols, idlecol)
                except:
                    pass

algorithms = ["naive", "not-so-naive", "linprog", 
              
              "g-fast", "g-short", "g-long", "g-economic", "g-earlycompletion", "g-makelongshort", "g-fastNeconomic", "g-shortNeconomic", "g-longNeconomic", "g-leasttotalusage", "g-longNeconomicNfast",
              
              "sg-fast", "g-short", "sg-long", "g-economic", "sg-earlycompletion", "sg-makelongshort", "sg-fastNeconomic", "sg-shortNeconomic", "sg-longNeconomic", "sg-leasttotalusage", "sg-longNeconomicNfast",
              
              "hf1", "hf2", 
              "hf3", "hf4"] 


def process_files(gdir, sgdir, hfgdir, lindir, ndir, nsndir):
    for alg in algorithms:
        out = open("stats-info"+"_"+alg,'w')
        buff = ""
        for numTasks in range(1, totalNumTasks + 1):
            for powerCap in range(1000, maxPowerCap, 400):
                try:
                    #fn = policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks)
                    if alg.startswith("g-"):
                        d = gdir
                    elif alg.startswith("sg-"):
                        d = sgdir
                    elif alg.startswith("hf"):
                        d = gdir
                    elif alg == "naive":
                        d = gdir
                    elif alg == "not-so-naive":    
                        d = gdir 
                    elif alg == "linprog":    
                        d = gdir   
                    
                    maxtime, totalarea, sumarea, wasted, idlearea = stats_info(fname)
                    
                    tab = "\t"
                    nl = "\n"
                    buff +=  + tab + powerCap + tab + numTasks + tab + nl
                except:
                    pass
                

                
                

f = "output/greedy/fast-1000-7"
draw(f, "fast-1000-7", colors, idleCol)






                
          
                
                
                
  
    
        
        

            
            
      
            
            
            

