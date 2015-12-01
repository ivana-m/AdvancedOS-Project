#smart greedy: fast, leasttotalusage, makelongshort, longNeconomicNfast
#naive
#halfhearted: 1


#import linprog
import greedy
import greedypolicies
import fileio
import rectangles
import os
import traceback

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
    if(n > 8 and n<26):
        n += 1    
    for i in range(0,n):
        if(i == 8): #the really slow filebound
            continue
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

totalNumTasks = 26
numMachines = 10
maxPowerCap = 4600
idlePow = 90.0
totalWkld = 10
idlestates = [1024] * numMachines
idleusage = [idlePow] * numMachines

policies = [greedypolicies.fast, greedypolicies.short, greedypolicies.economic, greedypolicies.earlycompletion, greedypolicies.fastNeconomic, greedypolicies.shortNeconomic, greedypolicies.leasttotalusage, greedypolicies.long, greedypolicies.makelongshort, greedypolicies.longNeconomic, greedypolicies.longNeconomicNfast]

policiesList = ["fast", "short", "economic", "earlycompletion", "fastNeconomic", "shortNeconomic", "leasttotalusage", "long", "makelongshort", "longNeconomic", "longNeconomicNfast"]


              
hfgreedy1 = [greedypolicies.economic, greedypolicies.leasttotalusage, greedypolicies.fast] 
hfgreedy2 = [greedypolicies.economic, greedypolicies.fast]

hfgreedy3 = [greedypolicies.economic, greedypolicies.leasttotalusage, greedypolicies.earlycompletion] 
hfgreedy4 = [greedypolicies.economic, greedypolicies.earlycompletion]

hf = [hfgreedy1, hfgreedy2, hfgreedy3, hfgreedy4]
hfList = ["comb1", "comb2", "comb3", "comb4"]


def create_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)    

def generate_files(master, dirN):
    for numTasks in range(1, totalNumTasks + 2):
        speed, pu = load_tasks(numTasks, numMachines, appd, idlePow)
        workload = [totalWkld] * numTasks
        for powerCap in range(1000, maxPowerCap, 400):
            try:
                newPath = os.path.join(master,dirN)
                #create_dir(newPath)
                #out = newPath+"-"+str(powerCap)+"-"+str(numTasks))
                nt = str(numTasks)
                if(numTasks > 8):
                    nt = str(numTasks - 1)                
                if(dirN == "greedy"):
                    for policy in policies:
                        newPath = os.path.join(newPath, policiesList[policies.index(policy)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+nt                  
                        order, trn, run = greedy.greedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                        newPath = os.path.join(master,dirN)
                elif(dirN == "smartGreedy"):
                    for policy in policies:
                        newPath = os.path.join(newPath, policiesList[policies.index(policy)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+nt                    
                        order, trn, run = greedy.smartGreedy(workload, speed, pu, idlestates, idleusage, powerCap, policy)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run)
                    newPath = os.path.join(master,dirN)
                    
                elif(dirN == "halfHeartedGreedy"):
                    for combo in hf:
                        newPath = os.path.join(newPath, hfList[hf.index(combo)])
                        create_dir(newPath)
                        out = newPath+"-"+str(powerCap)+"-"+nt                    
                        order, trn, run = greedy.halfHeartedGreedy(workload, speed, pu, idlestates, idleusage, powerCap, combo)
                        fileio.val2file(out, pu, idlestates, idleusage, powerCap, order, trn, run) 

            except:
                traceback.print_exc()
                pass
        
            

#sgenerate_files("output","smartGreedy")
#generate_files("output","greedy")
#generate_files("output", "halfHeartedGreedy")



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
def save_figure(fig, imgName, imgDir):
    fig.savefig(os.path.join(imgDir, imgName)+'.png', dpi='figure', bbox_inches='tight') 
    plt.close() #close plot - prevents plot from displaying. Use if generating many plots at once
    
def add_label(ax, text, x, y, fontsize):
    ax.text(x,y,text,fontsize=fontsize)
          
def draw(fname, dir, subdir, imgName, cols, idlecol):
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
    
    saveDir = os.path.join("imgOutput", dir, subdir)
    create_dir(saveDir)
    save_figure(fig, imgName, saveDir)
    
    

def stats_info(fname):
    tasks, machines, configs, pwrcap, mintime, maxtime, rects = fileio.file2rects(fname)
    sumarea = [0]
    idlearea = [0]
    def addAreas(i, j, k, x1, x2, y1, y2):
        sumarea[0] += (x2-x1) * (y2 - y1)
        if(i == tasks):
            idlearea[0] += (x2-x1) * (y2 - y1)
        
    
    rectangles.drawrects(rects, addAreas)
    
    totalarea = ((maxtime-mintime) * pwrcap)
    wasted = totalarea - sumarea[0]
    
    return maxtime, totalarea, sumarea[0], wasted, idlearea[0]
    
    


def draw_files(dir):
    #for policy in policies:
        #for numTasks in range(1, totalNumTasks + 1):
            #for powerCap in range(1000, maxPowerCap, 400):
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            try:
                #fn = policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks)
                fname = os.path.join(subdir, file)
                
                draw(fname, dir, subdir, file, colors, idleCol)
            except:
                traceback.print_exc()
                pass

algorithms = ["naive", "not-so-naive", "linprog", 
              
              "g-fast", "g-short", "g-long", "g-economic", "g-earlycompletion", "g-makelongshort", "g-fastNeconomic", "g-shortNeconomic", "g-longNeconomic", "g-leasttotalusage", "g-longNeconomicNfast",
              
              "sg-fast", "g-short", "sg-long", "g-economic", "sg-earlycompletion", "sg-makelongshort", "sg-fastNeconomic", "sg-shortNeconomic", "sg-longNeconomic", "sg-leasttotalusage", "sg-longNeconomicNfast",
              
              "hf1", "hf2", 
              "hf3", "hf4"] 


def process_files(dir):
   
    for subdir, dirs, files in os.walk(dir):
        for file in files:
            try:
                fname = os.path.join(subdir, file)
                numTasks = fname.split('-')[2]
                powerCap = fname.split('-')[1]
                saveDir = os.path.join("statsOutput",dir,subdir)
                create_dir(saveDir)
                outName = file.split('-')[0]
                maxtime, totalarea, sumarea, wasted, idlearea = stats_info(fname)
                t = '\t'
                nl = '\n'
                o = open(os.path.join(saveDir, outName), 'a')
                o.write(str(powerCap) + t + str(numTasks) + t+  str(maxtime) + t+ str(totalarea) + t+ str(sumarea) + t + str(wasted) + t +str(idlearea) + nl)
                o.close()
            except:
                traceback.print_exc()
                pass    
    
    
    #for alg in algorithms:
        #out = open("stats-info"+"_"+alg,'w')
        #buff = ""
        #for numTasks in range(1, totalNumTasks + 1):
            #for powerCap in range(1000, maxPowerCap, 400):
                #try:
                    ##fn = policiesList[policies.index(policy)]+"-"+str(powerCap)+"-"+str(numTasks)
                    #if alg.startswith("g-"):
                        #d = gdir
                    #elif alg.startswith("sg-"):
                        #d = sgdir
                    #elif alg.startswith("hf"):
                        #d = hfgdir
                    ##elif alg == "naive":
                    ##    d = gdir
                    ##elif alg == "not-so-naive":    
                    ##    d = gdir 
                    #elif alg == "linprog":    
                        #d = gdir   
                    
                    #maxtime, totalarea, sumarea, wasted, idlearea = stats_info(fname)
                    
                    #tab = "\t"
                    #nl = "\n"
                    #buff +=  + tab + powerCap + tab + numTasks + tab + nl
                #except:
                    #pass
                

         
#for subdir, dirs, files in os.walk("output/greedy"):
#    for file in files:

#        print(subdir, file)

#f = "output/greedy/fast/fast-1000-7"
#draw(f, "vlah", colors, idleCol)


def doAll(a):    
    #generate_files("output",a)
    #draw_files("output/"+a)
    process_files("output/"+a)
    
#doAll("greedy")
doAll("smartGreedy")
#doAll("halfHeartedGreedy")








                
          
                
                
                
  
    
        
        

            
            
      
            
            
            

