import matplotlib.pyplot as plt #use for drawing
import matplotlib.patches as patches #use for drawing

import os

class Task(object):
    
    def __init__(self, power, time, performance, startTime = 0, endTime = 0, currentPower = 0):
        self.requiredPower = float(power)
        self.time = float(time)
        self.allocatedPower = float(power)
        self.performance = float(performance)
        self.startTime = float(startTime)
        self.endTime = float(endTime)
        self.currentPower = float(currentPower)
        

outDir = "output/naive"

cols = ['#FF0000','#0000FF','#006400','#FFD700','#B22222','#4B0082','#008000','#FFA500','#800000','#008B8B','#808000','#DAA520','#FF00FF','#00FFFF','#00FF00','#D2691E','#FF1493','#008080','#556B2F','#D8BFD8','#8B4513','#000080','#00FF7F','#BDB76B','#CD5C5C','#1E90FF','#FF7F50']

idleCol = '0.5'


taskDir = "applications"
def new_line(task, var):
    tab = "\t"
    nl = "\n"
    x1 = str(task.startTime)
    x2 = str(task.endTime)
    y1 = str(task.currentPower)
    y2 = str(task.currentPower + task.requiredPower)
    col = str(var) 
    return x1 + tab + x2 + tab + y1 + tab + y2 + tab + col + nl

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
def save_figure(fig, imgName, imgDir):
    fig.savefig(os.path.join(imgDir, imgName)+'.png', dpi='figure', bbox_inches='tight') 
    plt.close() #close plot - prevents plot from displaying. Use if generating many plots at once
    
def add_label(ax, text, x, y, fontsize):
    ax.text(x,y,text,fontsize=fontsize)
    
def load_tasks(n):
    tasks = []
    if(n > 8 and n<26):
        n += 1
    for i in range(0,n):
        if(i == 8):
            continue
        taskFile = open(taskDir+"/"+str(i),'r')
        taskRuns = []
        for line in taskFile:
            properties = line.strip().split('\t')
            performance = properties[1]
            power = properties[2]
            time = properties[3]
            tsk = Task(power, time, performance)
            taskRuns.append(tsk)
        tasks.append(taskRuns)
        taskFile.close()
    return tasks

idleTask = Task(90,0,0)

def get_closestTask(taskFile, powerPerTask):
    minPowDiff = powerPerTask
    closestTask = None
    for task in taskFile:
        diff = powerPerTask
        if(task.requiredPower <= powerPerTask):
            diff = powerPerTask - task.requiredPower
            if(diff <= minPowDiff):
                minPowDiff = diff 
                closestTask = task
    if(closestTask is None):
        return idleTask
    else:
        return closestTask
    

def naive_simulator(tasks, numTasks, numMachines, powerCap):
    idleRuns = []   
    idleCurrPows = []    
    powerPerTask = powerCap / numTasks
    currentPower = 0
    remainingtasks = tasks
    newLines = []
    maxTime = 0
    run = 0
    totalMaxTime = 0
    if(numTasks <= numMachines):
        for taskFile in tasks:
            closestTask = get_closestTask(taskFile, powerPerTask)
            if(closestTask != idleTask):
                closestTask.currentPower = currentPower
                closestTask.startTime = 0
                closestTask.endTime = closestTask.time
                if(closestTask.endTime > maxTime):
                    maxTime = closestTask.endTime
                currentPower += closestTask.requiredPower
                col = cols[run % len(cols)]
                newLines.append(new_line(closestTask, col))
                
            else:
                idleRuns.append(run)
                idleCurrPows.append(currentPower)
                currentPower += 90
                newLines.append("")
            run += 1
        if(len(idleRuns) > 0):
            i = 0
            for idleRun in idleRuns:
                thisIdleTask = Task(90, maxTime, 0, 0, maxTime, idleCurrPows[i])
                i+=1
                newLines[idleRun] = new_line(thisIdleTask, idleCol)
        totalMaxTime = maxTime
    else: #more tasks than machines
        group = 0
        maxTime = 0
        startTime = 0
        scheduledTasks = 0
        tasksToSchedule = len(remainingtasks)
        while(scheduledTasks != tasksToSchedule):
            powerPerTask = powerCap / numMachines
            for m in range(0, numMachines):
                if(m + group < len(remainingtasks)):
                    
                    closestTask = get_closestTask(remainingtasks[m + group], powerPerTask)
                    
                    if(closestTask != idleTask):
                        closestTask.currentPower = currentPower
                        closestTask.startTime = startTime
                        closestTask.endTime = closestTask.time + startTime
                        if(closestTask.endTime > maxTime):
                            maxTime = closestTask.endTime
                        currentPower += closestTask.requiredPower
                        col = cols[(m+group) % len(cols)]
                        newLines.append(new_line(closestTask, col))
                        
                        scheduledTasks +=1
                        
                        #remainingtasks = remainingtasks[:(m+group)] + remainingtasks[(m+group+1):]
                        #print(len(remainingtasks))
                    else: #idletask
                        idleRuns.append(run)
                        idleCurrPows.append(currentPower)
                        currentPower += 90
                        newLines.append("")                    
                else: #idletask
                    idleRuns.append(run)
                    idleCurrPows.append(currentPower)
                    currentPower += 90
                    newLines.append("")
                run += 1
            if(len(idleRuns) > 0):
                i = 0
                for idleRun in idleRuns:
                    thisIdleTask = Task(90, maxTime, 0, startTime, startTime + maxTime, idleCurrPows[i])
                    i+=1
                    newLines[idleRun] = new_line(thisIdleTask, idleCol)
            
            group += numMachines
            currentPower = 0
            startTime = maxTime
            totalMaxTime += maxTime
            maxTime = 0
            
    
    outFileBuff = ""
    for line in newLines:
        outFileBuff += line
    return totalMaxTime, outFileBuff.strip()


totalNt = 26
maxPowerCap = 6600
numMachines = 3

def drawNstats_naive(buff, totalMaxTime, powerCap, numTasks):
    lines = buff.split('\n')
    sumArea = 0
    idleArea = 0
    t = "\t"
    nl = "\n"
    fig = init_figure()
    ax = fig.add_subplot(111)
    for line in lines:
        l = line.split('\t')
        if(len(l) > 0):
            x1 = float(l[0])
            x2 = float(l[1])
            y1 = float(l[2])
            y2 = float(l[3])
            col = l[4]
            sumArea += (x2-x1) * (y2 - y1)
            if(col == '0.5'):
                idleArea += (x2-x1) * (y2 - y1)
                add_idle_rectangle(ax, x1, y1, (x2-x1), (y2-y1), col)
            else:
                add_rectangle(ax, x1, y1, (x2-x1), (y2-y1), col)
    ax.axhline(y = powerCap, c = 'r', linewidth=1, zorder=5)
    plt.plot([totalMaxTime,totalMaxTime],[0,powerCap], '0.75')
    plt.ylabel("Power")
    plt.xlabel("Time")
    plt.title("naive; power cap: "+str(powerCap)+", #tasks: "+str(numTasks), fontsize = 14)
    save_figure(fig, "naive-"+str(powerCap)+"-"+str(numTasks), "imgOutput/naive")
    totalArea = powerCap * totalMaxTime
    wasted = totalArea - sumArea
    s = open("statsOutput/naive",'a')
    s.write(str(powerCap) + t + str(numTasks) + t + str(totalMaxTime) + t + str(totalArea) + t + str(sumArea) + t + str(wasted) + t + str(idleArea) + nl)
    s.close()
    
            

for numTasks in range(1, totalNt + 2):
    tasks = load_tasks(numTasks)
    for powerCap in range(1000, maxPowerCap, 400):
        nt = str(numTasks)
        if(numTasks > 8):
            nt = str(numTasks - 1)        
        totalMaxTime, buff = naive_simulator(tasks, numTasks, numMachines, powerCap)
        drawNstats_naive(buff, totalMaxTime, powerCap, numTasks)
        f = open("output/naive/"+"naive-"+str(powerCap)+"-"+nt, 'w')
        f.write(buff)
        f.close()
        

 
   