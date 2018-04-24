__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse application"

import cProfile
import memory_profiler
import csv
import sys
import graphtest
import networkx as nx
import itertools
import time
# import cProfile
# import matplotlib.pyplot as plt
# import pyqt_test


max_x=20
max_y=10
d=2 #distance between nodes along rack width
l=1 #rack

loc_dict = {}  # location according to id
shelf_dict ={}
orderlist = []
optorderlist = []
optorderdetail = []
pathnode = nx.Graph()
dist_dict = {}
# pathgraph = nx.Graph()
optoneordertemp = []
# readin products location
def readin():

    with open('warehouse-grid.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        max_x = 0
        max_y = 0
        for row in spamreader:
            pro_id = int(row[0])
            shelf_dict[pro_id] = [int(float(row[1])),int(float(row[2]))]
            pro_x = int(float(row[1])) * 2+1 #double the cordinates to simulate the path and move the rack from(0,0)to (1,1)
            pro_y = int(float(row[2])) * 2+1
            if pro_x>max_x:
                max_x = pro_x
            if pro_y>max_y:
                max_y = pro_y
            loc_dict[pro_id] = [pro_x, pro_y]
    print ("Total goods num:", len(loc_dict))
    max_x = (max_x-1)/2
    max_y = (max_y - 1) / 2
    print ("Max rack number in row, col", max_x, max_y)

#readin order number
def readorder(s):
    with open(s) as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            spamrow = row[0].split('\t')
            oneorder = []
            for element in spamrow:
                if element != '':
                    oneorder.append(int(element))
            orderlist.append(oneorder)
        # print orderlist

# find shortest distance between two points
def findpath(pathgraph,pro_id,init_x = 0, init_y = 0):
    pro_id = int(pro_id)
    if pro_id not in loc_dict:
        print ("id not exist")
        return -1

    pro_x = loc_dict[pro_id][0]     #x,y coordinates of products
    pro_y = loc_dict[pro_id][1]
    # print "Searching product id",pro_id, "product position", (pro_x,pro_y)
    # print "Calculating shortest path for one item......"


    #Product con only be taken from left or right, say east and west
    #if the product position is east to the current position i.e. init_x < prod_x
    if init_x < pro_x:
        des_x = pro_x - 1 #shorter to take from left path of the rack
        des_y = pro_y
        # if pro_x == 0:
        #     des_x = pro_x + 1 #can only take from right since its the boundary, say wall
        #     des_y = pro_y
    #if the product position is west to the current position i.e. init_x > prod_x
    elif init_x > pro_x:
        des_x = pro_x + 1 #shorter to take from right path of the rack
        des_y = pro_y
        # if pro_x == 20:
        #     des_x = pro_x - 1 #can only take from left since its the boundary, say wall
        #     des_y = pro_y
    else:
        des_x = init_x
        des_y = pro_y
    itemdistance,traversed= graphtest.locdistance(pathgraph,des_x, des_y,init_x,init_y)
    return itemdistance, des_x, des_y




def shortestdp(node,subset): #calculate from start
    #brute force
    '''if len(subset) == 0:

        return dist_dict[('start',node)]
    min = 10000
    templist = []
    temp = 0
    for ver in subset:
        templist = subset.copy()
        templist.remove(ver)
        temp = shortestdp(ver,templist) + dist_dict[(ver,node)] #node parent of vertex
        if temp<min:
            min = temp
            vertex_parent[node] = ver

    # print (vertex_parent)
    return min
    '''

    i=0
    vertex_par= {}
    laststep = 'start'

    #create 2-d matrix (item,steps):[minimum distance,from which item]
    for i in range(len(subset)):
        for elem in subset:
            mintemp = 10000
            if i == 0:
                vertex_par[(elem,i)]=[dist_dict[(node, elem)], laststep]#from start to every node

            else:
                for otherelem in set(subset)-{elem}:
                    if vertex_par[(otherelem,i-1)][0] + dist_dict[(elem,otherelem)]<mintemp:
                        mintemp = vertex_par[(otherelem,i-1)][0] + dist_dict[(elem,otherelem)]
                        othertemp = otherelem
                if mintemp<vertex_par[elem,i-1][0]:
                    mintemp=mintemp+2#might happen if they just separate by 1
                vertex_par[(elem,i)]= [mintemp,othertemp]

    min = 10000
    for elem in subset:#to end
       if  vertex_par[(elem,len(subset)-1)][0] + dist_dict[(elem,'end')]<min:
           min = vertex_par[(elem,len(subset)-1)][0] + dist_dict[(elem,'end')]
           elemtemp = elem
    vertex_par[(elemtemp, 'end')] = [min, elemtemp]


    print(vertex_par)

    optoneorder = []
    laststep = list(vertex_par).pop()
    dist = vertex_par[laststep][0]
    laststep = laststep[0]

    optoneorder.insert(0,laststep)#order second to last'end'
    for i in reversed(range(len(subset))):
        optoneorder.insert(0,vertex_par[(laststep,i)][1])#insert at head
        laststep = vertex_par[(laststep,i)][1]

    del optoneorder[0]
    return dist,optoneorder



#rearrange and optimize the order order
# compile with flag:python -m memory_profiler example.py
# @profile
def optimizeorder(pathgraph,oneorder,init_x,init_y,end_x,end_y):
    # construct graph and distance dictionary between graph
    ordergraph = nx.Graph()
    optoneorder = []
    orderloc = []
    ordergraph.add_node('start')
    ordergraph.add_node('end')
    for item_no in oneorder:
        orderloc.append(loc_dict[item_no])
        ordergraph.add_node(item_no)

        # calculate from these item to end or from original to these item
        d0, des_x, des_y = findpath(pathgraph,item_no,init_x,init_y)#from original is 'start'
        dist_dict[('start',item_no)] = d0
        df,traversed= graphtest.locdistance(pathgraph,end_x,end_y,des_x,des_y)#to end
        dist_dict[(item_no,'end')] = df
        ordergraph.add_edge('start', item_no,length = d0)
        ordergraph.add_edge('end', item_no,length = df)
    '''
    # Dynamic programming
    print("Dynamic programming shortest distance to travel ......")

    nodespair = list(itertools.combinations(oneorder, 2))
    ordergraph.add_edges_from(nodespair)
    # heuristics,not known:start from nowhere? distance between 2 items,+-1
    for pair in nodespair:
        d, des_x, des_y = findpath(pair[0])
        pathlength, x, y = findpath(pair[1], des_x, des_y)
        # add graph edge
        ordergraph.add_edge(pair[0], pair[1], length=pathlength)
        dist_dict[(pair[0], pair[1])] = pathlength
        dist_dict[(pair[1], pair[0])] = pathlength

    # solving dsp problem recursively
    start = time.time()

    min,optoneorder= shortestdp('start',oneorder)



    print('Minimum travel distance: ', min, ',in order of: ', 'start from ', (init_x, init_y), optoneorder, ', end at ',
          (end_x, end_y))
    loclist = []
    for item in optoneorder:
        print('go to shelf:', shelf_dict[item], 'on location:', loc_dict[item], 'pick up item:', item, ', then ', )
    # measure time
    end = time.time()
    print('drop off at:', [end_x, end_y])
    print('Dynamic programming cost:', end - start)

    '''
    # nearest neighbor
    print("Computing greedily shortest distance to travel ......")
    start = time.time()
    # nodespair = list(itertools.combinations(oneorder, 2))
    # ordergraph.add_edges_from(nodespair)
    # # heuristics,not known:start from nowhere? distance between 2 items,+-1
    # for pair in nodespair:
    #     d, des_x, des_y = findpath(pair[0])
    #     pathlength, x, y = findpath(pair[1], des_x, des_y)
    #     # add graph edge
    #     ordergraph.add_edge(pair[0], pair[1], length=pathlength)
    #     dist_dict[(pair[0], pair[1])] = pathlength
    #     dist_dict[(pair[1], pair[0])] = pathlength

    itemtemp = 0
    mindist = 0
    x=init_x
    y=init_y
    temp_x=None
    temp_y=None
    while oneorder !=[]:
        min = 10000
        for item in oneorder:
            pathlength, des_x, des_y = findpath(pathgraph,item, x, y)

            if pathlength<min:
                min = pathlength
                itemtemp = item
                temp_x=des_x
                temp_y=des_y


        optoneorder.append(itemtemp)
        oneorder.remove(itemtemp)
        mindist = mindist + min
        x=temp_x
        y=temp_y
    mindist = mindist + graphtest.locdistance(pathgraph,end_x,end_y,x,y)[0]#to drop off point

    print('Minimum travel distance: ', mindist, ',in order of: ', 'start from ', (init_x, init_y), optoneorder, ', end at ',
          (end_x, end_y))
    loclist = []
    for item in optoneorder:
        print('go to shelf:', shelf_dict[item], 'on location:', loc_dict[item], 'pick up item:', item, ', then ', )
    # measure time
    end = time.time()
    print('drop off at:', [end_x, end_y])
    print('Nearest neighbor cost:', end - start)
    min = mindist

    '''
    # brute force compute optimized order
    print ("Computing brute force shortest distance to travel ......")

    start = time.time()
    nodespair = list(itertools.combinations(oneorder, 2))
    ordergraph.add_edges_from(nodespair)
    # heuristics,not known:start from nowhere? distance between 2 items,+-1
    for pair in nodespair:
        d,des_x,des_y = findpath(pair[0])
        pathlength,x,y= findpath(pair[1],des_x,des_y)
        # add graph edge
        ordergraph.add_edge(pair[0], pair[1], length = pathlength)
        dist_dict[(pair[0], pair[1])] = pathlength
        dist_dict[(pair[1], pair[0])] = pathlength
        # print "shortest distance between ",(pair[0], pair[1])," ",pathlength
    # print dist_dict
    # distances between pairs calculated, brute force calculate shortest travelling order
    # brute force
    possiblepath = list(itertools.permutations(oneorder))
    # print 'possible path: ', possiblepath
    min = 1000000
    dist = 0

    for p in possiblepath:
        for item in range(len(p)-1):
            if item == 0:
                dist = dist_dict[('start',p[item])]# distance from start to first product
            dist = dist+dist_dict[(p[item], p[item+1])]
            # print (p[item], p[item+1])
        dist = dist + dist_dict[(p[item+1], 'end')]#distance to drop off point
        if dist< min:
            min = dist
            optoneorder = list(p)
        dist = 0
    print ('Minimum travel distance: ',min,',in order of: ', 'start from ',(init_x,init_y),optoneorder,', end at ',(end_x,end_y))
    loclist = []
    for item in optoneorder:
        print( 'go to shelf:',shelf_dict[item],'on location:', loc_dict[item], 'pick up item:',item, ', then ',)
    # measure time
    end = time.time()
    print ('drop off at:', [end_x,end_y])
    print('Brute force cost:', end - start)
    '''
    return optoneorder,min

def originalorder(pathgraph,oneorder,x_init,y_init,x_end,y_end):
    # original order
    dist_oneorder = 0
    for item in oneorder:
        dist, x_des, y_des = findpath(pathgraph,item,x_init,y_init)
        x_init = x_des
        y_init = y_des
        dist_oneorder = dist_oneorder + dist
        # print
    # back to end point

    # print"returning to end point......"
    backtrip,traversed= graphtest.locdistance(pathgraph,x_init,y_init,x_end,y_end)
    dist_oneorder = dist_oneorder + backtrip

    print ('Distance for one order without optimization', dist_oneorder)
    return dist_oneorder


def singleOrder(pathgraph,oneorder,x_init,y_init,x_end,y_end):
    if oneorder == None:
        oneorder = []
        orderlist = input("Hello User, what items would you like to pick?: use tab to separate: ")
        spamorderlist = orderlist.split('\t')

        for element in spamorderlist:
            oneorder.append(int(element))
    print ('The order ready to pick: ', oneorder)
    print()
    # nextline for time profiling
    #     oneorder=[427230,372539,396879,391680,208660,105912,332555,227534,68048,188856,736830,736831,479020,103313,365797,97077,117900,384900,769581,1372184,226774]
    #     oneorder = [176484,245818,195946,272457,354111,103926,106685,260033,306104,397673,16643,193618,180958,226774,392017,154454,287261,111873,391857,393069,1400578]
    #     oneorder=[337003,394165,309096,383371,176484,1190168,71795,41100,204756,96509,1588730,239436,151579,285408,34182,306176,180023,32895,191515,327710,156753]

    dist_org=originalorder(pathgraph,oneorder,x_init,y_init,x_end,y_end)
    orig=[]
    for element in oneorder:
        orig.append(element)

    optoneorder,mintravel=optimizeorder(pathgraph,oneorder,x_init,y_init,x_end,y_end)

    return orig,dist_org,optoneorder,mintravel

def createpathg(max_x=18,max_y=10,d=2 ,l=1 ):

    # write path graph:
    i = 0
    pathgraph = nx.Graph()

    # create graph
    # add nodes
    for c in range(2 * max_x + 1):
        if c % 2 == 0:
            for r in range(2 * max_y + 1):
                pathgraph.add_node(i, coordinate=[c, r])
                i = i + 1
                # print [c,r]
    # print pathgraph.nodes
    # add edges
    # vertical edges
    for c in range(max_x):
        for i in range(max_y * 2):
            pathgraph.add_edge(c * (2 * max_y + 1) + i, c * (2 * max_y + 1) + i + 1, distance=1)
    # horizontal edges
    for r in range(0, 2 * max_y + 1, 2):
        for c in range(max_x):
            pathgraph.add_edge(c * (2 * max_y + 1) + r, (c + 1) * (2 * max_y + 1) + r, distance=2)
    # print pathgraph.edges
    # end pathgraph

    # draw


    return pathgraph

def inputpara():

    x_init, y_init = input("Hello User, where is your worker? please enter: x,y:  if exceeds,default 0,0 \n > ").split(
        ',')
    # print type(x_init) is not int or type(x_init) is not int or x_init > 36 or y_init > 20
    if type(x_init) is not int or type(x_init) is not int or x_init > 36 or y_init > 20:
        x_init = 0
        y_init = 0
    x_end, y_end = input("What is your worker's end location? please enter x,y:  if exceeds, default 0,20 \n > ").split(
        ',')
    # print type(x_end) is not int or type(x_end) is not int or x_end > 36 or y_end > 20
    if type(x_end) is not int or type(x_end) is not int or x_end > 36 or y_end > 20:
        x_end = 0
        y_end = 20
    return x_init, y_init, x_end, y_end

def processorder(pathgraph,x_init, y_init, x_end, y_end):
    choice = input("Hello User, input manually: yes? no?")
    if choice == "yes" or choice == "Yes" or choice == "YES":
        # input single order
        org, origl, opt, min = singleOrder(pathgraph,None, x_init, y_init, x_end, y_end)
        # cProfile.run("org, origl, opt, min = singleOrder(None, x_init, y_init, x_end, y_end)", sort="cumulative")
        print('write into file......')
        i = 0
        optorderfile = input("Please list output file name: \n >")
        title = ['Order number:'] + [i]
        optorderdetail.append(title)
        start = ['Start location:'] + [(x_init, y_init)]
        optorderdetail.append(start)
        end = ['End location:'] + [(x_end, y_end)]
        optorderdetail.append(end)
        origorder = ['Original order:   '] + org
        optorderdetail.append(origorder)
        opt = ['Optimized order:'] + opt
        optorderdetail.append(opt)
        dist1 = ['Original parts distance:'] + [origl]
        optorderdetail.append(dist1)
        dist2 = ['Optimized parts distance:'] + [min]
        optorderdetail.append(dist2)
        writeorderfile(optorderdetail, optorderfile)

        i = i + 1
        print('Writing into file......')
    else:
        optorderfile = input("Please list order file name: \n >")
        readorder(optorderfile)
        # for oneorder in orderlist:
        optorderfile = input("Please list output file name: \n >")

        for i in range(0,len(orderlist)):
            oneorder = orderlist[i]
            org,origl,opt,min=singleOrder(pathgraph,oneorder,x_init, y_init, x_end, y_end)
            print ("number processed:",i+1)
            optorderlist.append(opt)

            title = ['Order number:'] + [i]
            optorderdetail.append(title)
            start = ['Start location:'] + [(x_init, y_init)]
            optorderdetail.append(start)
            end = ['End location:'] + [(x_end, y_end)]
            optorderdetail.append(end)
            origorder = ['Original order:   '] + org
            optorderdetail.append(origorder)
            opt = ['Optimized order:'] + opt
            optorderdetail.append(opt)
            dist1 = ['Original parts distance:'] + [origl]
            optorderdetail.append(dist1)
            dist2 = ['Optimized parts distance:'] + [min]
            optorderdetail.append(dist2)
        writeorderfile(optorderdetail, optorderfile)



        print('write into file......')






def writeorderfile(a,file):
    with open(file, "a") as my_csv:

        csvWriter = csv.writer(my_csv, delimiter='\t')
        csvWriter.writerows(a)

if __name__ == '__main__':



    #cProfile.run("readin()", sort="cumulative")
    readin()


    pathgraph = nx.Graph()
    # cProfile.run("pathgraph = createpathg(max_x,max_y,2,1)", sort="cumulative")
    pathgraph = createpathg(max_x,max_y,2,1)


    x_init, y_init, x_end, y_end = inputpara()

    processorder(pathgraph,x_init, y_init, x_end, y_end)



    # #test
    # a = [[1, 2, 3, 4], [2, 3, 234, 5, 643, 4, 4]]
    # writeorderfile(optorderlist, a)
    # dist = findpath(45, x_init, y_init)
    #
    print
    print



