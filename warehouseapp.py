__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse application"



import cProfile
import memory_profiler
import csv
import sys
import graphtest
from graphplot import *
import networkx as nx
import itertools
import time
import matplotlib.pyplot as plt
from copy import deepcopy
from math import inf

# import cProfile
# import matplotlib.pyplot as plt
# import pyqt_test


max_x=20
max_y=10
d=2 #distance between nodes along rack width
l=1 #rack

loc_dict = {}  # location according to id
shelf_dict ={}

iteminfo_dict={}
orderlist = []
optorderlist = []
optorderdetail = []
pathnode = nx.Graph()
dist_dict = {}
treenode_dict = {}
# pathgraph = nx.Graph()

# readin products location
def readin():
    # read order location
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
    count=0
    #read item information
    with open("item-dimensions-tabbed.txt") as bookfile:
        alist = [line.rstrip() for line in bookfile]

        for line in alist:
            row = line.split("\t")
            if count==0:
                count=count+1
                continue

            iteminfo_dict[int(row[0])]={}
            iteminfo_dict[int(row[0])]['weight']=float(row[4])
            iteminfo_dict[int(row[0])]['length'] = float(row[1])
            iteminfo_dict[int(row[0])]['width'] = float(row[2])
            iteminfo_dict[int(row[0])]['height'] = float(row[3])
            count=count+1
    print("Total item number:",count-1)

#readin order number batchful of reader
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
    # orderloc = []
    ordergraph.add_node('start',pos=(init_x,init_y))
    ordergraph.add_node('end',pos=(end_x,end_y))

    for item_no in oneorder:
        ordergraph.add_node(item_no, pos=(loc_dict[item_no][0], loc_dict[item_no][1]))
        # orderloc.append(loc_dict[item_no])
        # calculate from these item to end or from original to these item
        d0, des_x, des_y = findpath(pathgraph,item_no,init_x,init_y)#from original is 'start'
        dist_dict[('start',item_no)] = d0
        df,traversed= graphtest.locdistance(pathgraph,end_x,end_y,des_x,des_y)#to end
        dist_dict[(item_no,'end')] = df
        ordergraph.add_edge('start', item_no,weight = d0)
        ordergraph.add_edge('end', item_no,weight = df)
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
    '''
    #debug use, calculate lower bound print minimum spanning tree
    if __debug__:
        print("Calculating lower bound......")
        nodespair = list(itertools.combinations(oneorder, 2))

        # heuristics,not known:start from nowhere? distance between 2 items,+-1
        for pair in nodespair:
            pro_x = loc_dict[pair[0]][0]  # x,y coordinates of products
            pro_y = loc_dict[pair[0]][1]
            pathlength, xtmp, ytmp = findpath(pathgraph,pair[1],pro_x-1,pro_y)
            # add graph edge
            ordergraph.add_edge(pair[0], pair[1], weight=pathlength)
        print (ordergraph.edges(data=True))
        pos = nx.get_node_attributes(ordergraph, 'pos')
        nx.draw_networkx(ordergraph,pos)
        labels = nx.get_edge_attributes(ordergraph, 'weight')
        nx.draw_networkx_edge_labels(ordergraph, pos, edge_labels=labels)
        plt.show(block=False)
        time.sleep(5)
        plt.close()
        T = nx.minimum_spanning_tree(ordergraph)
        print(T.edges(data=True))
        pos = nx.get_node_attributes(T, 'pos')
        nx.draw_networkx(T, pos)
        labels = nx.get_edge_attributes(T, 'weight')
        nx.draw_networkx_edge_labels(T, pos, edge_labels=labels)
        plt.show()

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

    x=init_x
    y=init_y
    temp_x=None
    temp_y=None
    itemshift = 0
    oneordertemp=[]
    optoneordertemp = []
    mindist=10000
    init_x_l=0
    init_y_l=0
    for i in range(len(oneorder)-1):
        itemshift = oneorder.pop(0)
        oneorder.append(itemshift)
        oneordertemp=oneorder[:]
        print("after shift:",oneorder)
        mindisttemp = 0
        while oneorder !=[]:
            min = 10000
            for item in oneorder:
                pathlength, des_x, des_y = findpath(pathgraph,item, x, y)

                if pathlength<min:
                    min = pathlength
                    itemtemp = item
                    temp_x=des_x
                    temp_y=des_y


            optoneordertemp.append(itemtemp)
            oneorder.remove(itemtemp)
            mindisttemp = mindisttemp + min
            x=temp_x
            y=temp_y
        mindisttemp=mindisttemp+graphtest.locdistance(pathgraph,end_x,end_y,x,y)[0]#to drop off point
        print("mindist:",mindisttemp)
        print("one optimized:",optoneordertemp)
        if mindisttemp<mindist:
            mindist=mindisttemp
            init_x_l=x
            init_y_l=y
            optoneorder=optoneordertemp[:]

        oneorder=oneordertemp[:]
        optoneordertemp = []
        oneordertemp=[]
        x = init_x
        y = init_y

    print('Minimum travel distance: ', mindist, ',in order of: ', 'start from ', (init_x, init_y), optoneorder, ', end at ',
          (end_x, end_y))

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

def matrixredu(matrix):#both matrix and cost are returned
    mincost=0
    cost=0
    k=0
    matred=[]

    # reduce by row
    for row in matrix:
        if len([i for i in row if i is not inf])==0 or min(i for i in row) == 0:
            matred.append(row)
        else:
            matred.append([])
            mincost = min(i for i in row )
            for ele in row:
                if ele != inf:
                    matred[k].append(ele-mincost)
                else:
                    matred[k].append(inf)
            cost = cost +mincost
        k=k+1

    #reduce by col
    for i in range(len(matred[0])):
        if 0 in [row[i] for row in matred]:
            continue
        else:
            # if len([i for i in matred[i] if i is not None])!=0:
            if len([n for n in [row[i] for row in matred] if n is not inf])== 0 :#all col is none

                continue
            else:
                mincost = min(n for n in [row[i] for row in matred] if n is not inf)
                cost=cost + mincost
                for j in range(len(matred)):
                    if matred[j][i]== inf:
                        continue
                    matred[j][i] = matred[j][i]-mincost



    return matred,cost



#optimize order use branch and bound methods
def branchnbound(pathgraph, oneorder, init_x, init_y, end_x, end_y):
    # construct graph and distance dictionary between graph
    ordergraph = nx.Graph()
    optoneorder = []
    matrix=[[inf]]
    redumatrix=[]
    subcost=0
    ordergraph.add_node('start', pos=(init_x, init_y))
    ordergraph.add_node('end', pos=(end_x, end_y))

    for item_no in oneorder:
        ordergraph.add_node(item_no, pos=(loc_dict[item_no][0], loc_dict[item_no][1]))
        # calculate from these item to end or from original to these item
        d0, des_x, des_y = findpath(pathgraph, item_no, init_x, init_y)  # from original is 'start'
        dist_dict[('start', item_no)] = d0
        df, traversed = graphtest.locdistance(pathgraph, end_x, end_y, des_x, des_y)  # to end
        dist_dict[(item_no, 'end')] = df
        ordergraph.add_edge('start', item_no, weight=d0)
        ordergraph.add_edge('end', item_no, weight=df)
        matrix[0].append(d0)#source to distination  horizontal add
        matrix.append([d0]) #vertical add



    nodespair = list(itertools.combinations(oneorder, 2))
    ordergraph.add_edges_from(nodespair)
    # heuristics,not known:start from nowhere? distance between 2 items,+-1
    i=1
    for item in oneorder:
            for another in oneorder:
                if another ==item:
                    matrix[i].append(inf)
                    continue
                pro_x1 = loc_dict[another][0]  # x,y coordinates of products
                pro_y1 = loc_dict[another][1]
                pro_x2 = loc_dict[item][0]  # x,y coordinates of products
                pro_y2 = loc_dict[item][1]
                pathlength = graphtest.locdistance(pathgraph, pro_x2 - 1, pro_y2, pro_x1 - 1, pro_y1)
                ordergraph.add_edge(item,another, weight=pathlength[0])
                matrix[i].append(pathlength[0])
            i=i+1
    # print('Original distance')
    # for row in matrix:
    #     print(row)
    start = time.time()
    print("Computing shortest distance to travel using branch and bound......")

    # algorithm begins here-----------------------------------------------------------------------------------------
    # priority queue for min cost value node using heapq
    level=0
    nodenum=0
    itemcurr=None
    pathtemp=[]

    # initial reduce from starting point
    redumatrix,initcost=matrixredu(matrix)
    # add root node to dict
    treenode_dict[nodenum]=[initcost,deepcopy(redumatrix),level,0,None,[]]#root node cost,matrix,number visited,current item,path
    print("initial matrix")
    for row in matrix:
        print(row)
    print("initial cost",initcost)
    # # calculate from start to other node:
    while len(treenode_dict)!=0:
        minnode =min(treenode_dict, key=lambda k: treenode_dict[k])

        #modify min cost key to be the largest level if several same costs occurred in diff level
        costtemp=treenode_dict[minnode][0]
        leveltemp=0
        for item in treenode_dict:
            if treenode_dict[item][0]==costtemp:
                if treenode_dict[item][2]>leveltemp:
                    leveltemp=treenode_dict[item][2]
                    minnode=item

        itemcurr=treenode_dict[minnode][3]
        level=treenode_dict[minnode][2]
        # matrixtemp=deepcopy(treenode_dict[minnode][1])
        pathtemp = deepcopy(treenode_dict[minnode][5])
        pathtemp.append(itemcurr)

    #     redumatrixtemp, optchoice, cost = reduroutine(redumatrix, src, oneordertemptemp, oneorder, initcost, optoneordertemp)


        for des in range(len(oneorder)+1):
            # if des in pathtemp:
            #     continue# pass if traversed in current path
            if treenode_dict[minnode][1][itemcurr][des] !=inf and des not in pathtemp:
                print('new node ',nodenum+1,'----------------------------------------')
                nodenum=nodenum+1
            #set row and col

                redumatrixtemp=deepcopy(redumatrix)
                redumatrixtemp[itemcurr]=[inf]*len(redumatrixtemp)      #set source row to inf
                for i in range(len(redumatrixtemp)):
                    redumatrixtemp[i][des]=inf                 #set des col to inf

                redumatrixtemp[des][0] = inf            #set dest->src to inf

                # print("child to be reduced")
                # for row in redumatrixtemp:
                #     print(row)
                # #reduce child matrix
                redumatrixchild,costchild=matrixredu(deepcopy(redumatrixtemp))
                # print("child reduced")
                #
                # for row in redumatrixchild:
                #     print(row)
                # print("child cost", costchild)


                print("path before:",pathtemp)
                costtemp=treenode_dict[minnode][0]+treenode_dict[minnode][1][itemcurr][des]+costchild #child->redumatrix
                treenode_dict[nodenum] =[costtemp,deepcopy(redumatrixtemp),level+1,des,treenode_dict[minnode][3],deepcopy(pathtemp)]
                print("cost:",costtemp,"parent:",itemcurr,"parent node:",minnode,"child",des,"level",level+1)



        if treenode_dict[nodenum][2]==len(oneorder): #if all items reached return mincost

            end = time.time()
            print("branch and bound cost:", end-start)
            # pathtemp.append(treenode_dict[minlastcost][3])
            # minlastcost=min(treenode_dict, key=lambda k: treenode_dict[k])
            print("Shortest path:",treenode_dict[nodenum][5],"Last node:",treenode_dict[nodenum][3],"its parent:",treenode_dict[nodenum][4])
            print("upper bound:",treenode_dict[nodenum][0])
            print("final matrix")
            for row in treenode_dict[nodenum][1]:
                print(row)
            pathtemp.append(treenode_dict[nodenum][3])
            pathtemp.pop(0)
            for item in pathtemp:
                optoneorder.append(oneorder[item-1])

            mindist=treenode_dict[nodenum][0]#!!!!!!!!!!!!!!!!!!!
            # print out path
            print('Minimum travel distance: ', mindist, ',in order of: ', 'start from ', (init_x, init_y), optoneorder,
                  ', end at ',
                  (end_x, end_y))

            for item in optoneorder:
                print('go to shelf:', shelf_dict[item], 'on location:', loc_dict[item], 'pick up item:', item,
                      ', then ', )
            # measure time

            print('drop off at:', [end_x, end_y])
            print('Branch and bound cost:', end - start)

            return optoneorder, mindist

            # return treenode_dict[minnode][],treenode_dict[minnode][0]

        del treenode_dict[minnode]
        del minnode






    # algorithm ends here---------------------------------

def computeeffort(pathgraph,optoneorder,x_init,y_init,x_end,y_end):
    totaleffort=0
    totalweight=0
    count=0
    distemp=0
    for id in optoneorder:
        if id not in iteminfo_dict:
            print("no dimension information of such item id:",id,"set default weight 0.1")
            iteminfo_dict[id]={}
            iteminfo_dict[id]['weight'] = 0.1

        if count==0:
            distemp, x_des, y_des = findpath(pathgraph, id, x_init, y_init)
            x_init = x_des
            y_init = y_des
            totalweight=totalweight+iteminfo_dict[id]['weight']
            count=count+1
            continue

        distemp,x_des,y_des=findpath(pathgraph,id,x_init,y_init)
        totaleffort = totaleffort + distemp * totalweight

        totalweight = totalweight + iteminfo_dict[id]['weight']
        x_init=x_des
        y_init=y_des
        count=count+1




    distemp,temp=graphtest.locdistance(pathgraph,x_end,y_end,x_init,y_init)

    totaleffort = totaleffort + distemp * totalweight

    print("total effort",round(totaleffort,1))
    return round(totaleffort,1)



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
    # choice=2
    choice = 1#int(input("Please choose algorithm, 1 for nearest neighbor, 2 for branch and bound:"))
    if choice==1:#nearest neighbor
        optoneorder, mintravel = optimizeorder(pathgraph, oneorder, x_init, y_init, x_end, y_end)
    elif choice==2:#branch and bound
        optoneorder, mintravel = branchnbound(pathgraph, oneorder, x_init, y_init, x_end, y_end)


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
    x_init=int(x_init)
    y_init=int(y_init)
    # print type(x_init) is not int or type(x_init) is not int or x_init > 36 or y_init > 20
    if x_init > 36 or y_init > 20:
        x_init = 0
        y_init = 0
    x_end, y_end = input("What is your worker's end location? please enter x,y:  if exceeds, default 0,20 \n > ").split(
        ',')
    # print type(x_end) is not int or type(x_end) is not int or x_end > 36 or y_end > 20
    x_end=int(x_end)
    y_end=int(y_end)
    if  x_end > 36 or y_end > 20:
        x_end = 0
        y_end = 20

    return x_init, y_init, x_end, y_end

def processorder(pathgraph,x_init, y_init, x_end, y_end):
    choice = input("Hello User, input manually: yes? no?")
    if choice == "yes" or choice == "Yes" or choice == "YES":
        # input single order
        org, origl, opt, min = singleOrder(pathgraph,None, x_init, y_init, x_end, y_end)
        # cProfile.run("org, origl, opt, min = singleOrder(None, x_init, y_init, x_end, y_end)", sort="cumulative")

        #compute effort
        effortslct = int(input("Whether compute effort? 1 for yes, 2 for no"))
        if effortslct == 1:
            totaleffort=computeeffort(pathgraph,opt,x_init,y_init,x_end,y_end)

        print('write into file......')
        i = 0
        optorderfile = input("Please list output file name: \n >")
        title = ['Order number:'] + [i]
        optorderdetail.append(title)
        start = ['Start location:'] + [x_init, y_init]
        optorderdetail.append(start)
        end = ['End location:'] + [x_end, y_end]
        optorderdetail.append(end)
        origorder = ['Original order:   '] + org
        optorderdetail.append(origorder)
        opt = ['Optimized order:'] + opt
        optorderdetail.append(opt)
        dist1 = ['Original parts distance:'] + [origl]
        optorderdetail.append(dist1)
        dist2 = ['Optimized parts distance:'] + [min]
        optorderdetail.append(dist2)
        effortterm = ['Total effort:'] + [totaleffort]
        optorderdetail.append(effortterm)
        writeorderfile(optorderdetail, optorderfile)

        i = i + 1
        print('Writing into file......')
    else:
        optorderfile = input("Please list order file name: \n >")
        readorder(optorderfile)
        # for oneorder in orderlist:
        optorderfile = input("Please list output file name: \n >")
        effortslct = int(input("Whether compute effort? 1 for yes, 2 for no"))
        for i in range(0,len(orderlist)):
            oneorder = orderlist[i]
            org,origl,opt,min=singleOrder(pathgraph,oneorder,x_init, y_init, x_end, y_end)
            if effortslct == 1:
                totaleffort = computeeffort(pathgraph, opt, x_init, y_init, x_end, y_end)

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
            effortterm = ['Total effort:'] + [totaleffort]
            optorderdetail.append(effortterm)

        writeorderfile(optorderdetail, optorderfile)



        print('write into file......')






def writeorderfile(a,file):
    with open(file, "a") as my_csv:

        csvWriter = csv.writer(my_csv, delimiter='\t')
        csvWriter.writerows(a)

if __name__ == '__main__':



    #cProfile.run("readin()", sort="cumulative")

    readin()

    # '''
    pathgraph = nx.Graph()
    # cProfile.run("pathgraph = createpathg(max_x,max_y,2,1)", sort="cumulative")
    pathgraph = createpathg(max_x, max_y, 2, 1)
    x_init, y_init, x_end, y_end = inputpara()

    processorder(pathgraph, x_init, y_init, x_end, y_end)

    # '''

    # #test
    # a = [[1, 2, 3, 4], [2, 3, 234, 5, 643, 4, 4]]
    # writeorderfile(optorderlist, a)
    # dist = findpath(45, x_init, y_init)
    #
    print
    print



