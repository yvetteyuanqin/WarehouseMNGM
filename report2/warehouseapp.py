__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse application"


import csv
import sys
import graphtest
import networkx as nx
import itertools
import time

loc_dict = {}  # location according to id
shelf_dict ={}
orderlist = [];
optorderlist = [];
pathnode = nx.Graph()
dist_dict = {}

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
    print "Total goods num:", len(loc_dict)
    max_x = (max_x-1)/2
    max_y = (max_y - 1) / 2
    print "Max rack number in row, col", max_x, max_y

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
def findpath(pro_id,init_x = 0, init_y = 0):
    pro_id = int(pro_id)
    if pro_id not in loc_dict:
        print "id not exist"
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
    itemdistance = graphtest.pathgraph(des_x, des_y,init_x,init_y)
    return itemdistance, des_x, des_y




#rearrange and optimize the order order
def optimizeorder(oneorder,init_x,init_y,end_x,end_y):
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
        d0, des_x, des_y = findpath(item_no)#from original
        dist_dict[('start',item_no)] = d0
        df = graphtest.pathgraph(end_x,end_y,des_x,des_y)
        dist_dict[(item_no,'end')] = df
        ordergraph.add_edge('start', item_no,length = d0)
        ordergraph.add_edge('end', item_no,length = df)

    # brute force compute optimized order
    print "Computing shortest distance to travel ......"
    print
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
    print 'Minimum travel distance: ',min,',in order of: ', 'start from ',(init_x,init_y),optoneorder,', end at ',(end_x,end_y)
    loclist = []
    for item in optoneorder:
        print 'go to shelf:',shelf_dict[item],'on location:', loc_dict[item], 'pick up item:',item, ', then ',
    # measure time
    end = time.time()
    print 'drop off at:', [end_x,end_y]
    print'Brute force cost:', end - start
    return optoneorder,min

def originalorder(oneorder,x_init,y_init,x_end,y_end):
    # original order
    dist_oneorder = 0
    for item in oneorder:
        dist, x_des, y_des = findpath(item,x_init,y_init)
        x_init = x_des
        y_init = y_des
        dist_oneorder = dist_oneorder + dist
        # print
    # back to end point

    # print"returning to end point......"
    backtrip = graphtest.pathgraph(x_init,y_init,x_end,y_end)
    dist_oneorder = dist_oneorder + backtrip

    print 'Distance for one order without optimization', dist_oneorder
    return dist_oneorder


def singleOrder(oneorder,x_init,y_init,x_end,y_end):
    if oneorder == None:
        oneorder = []
        orderlist = raw_input("Hello User, what items would you like to pick?: use tab to separate: ")
        spamorderlist = orderlist.split('\t')

        for element in spamorderlist:
            oneorder.append(int(element))
    print 'The order ready to pick: ', oneorder

    dist_org=originalorder(oneorder,x_init,y_init,x_end,y_end)

    optoneorder,mintravel=optimizeorder(oneorder,x_init,y_init,x_end,y_end)

    return oneorder,dist_org,optoneorder,mintravel


def writeorderfile(a,file):
    with open(file, "a") as my_csv:

        csvWriter = csv.writer(my_csv, delimiter='\t')
        csvWriter.writerows(a)

if __name__ == '__main__':
    print
    print

    readin()
    choice = raw_input("Hello User, input manually: yes? no?")
    x_init, y_init = input("Hello User, where is your worker? please enter: x,y:  if exceeds,default 0,0 \n > ")
    # print type(x_init) is not int or type(x_init) is not int or x_init > 36 or y_init > 20
    if type(x_init) is not int or type(x_init) is not int or x_init > 36 or y_init > 20:
        x_init = 0
        y_init = 0
    x_end, y_end = input("What is your worker's end location? please enter x,y:  if exceeds, default 0,20 \n > ")
    # print type(x_end) is not int or type(x_end) is not int or x_end > 36 or y_end > 20
    if type(x_end) is not int or type(x_end) is not int or x_end > 36 or y_end > 20:
        x_end = 0
        y_end = 20


    if choice == "yes" or choice == "Yes" or choice == "YES":
        # input single order
        org,origl,opt,min = singleOrder(None,x_init,y_init,x_end,y_end)
        print 'write into file......'
        i=1
        optorderfile = raw_input("Please list output file name: \n >")
        title = ['Order number:'] + [i]
        optorderlist.append(title)
        start = ['Start location:'] + [(x_init,y_init)]
        optorderlist.append(start)
        end = ['End location:'] + [(x_end,y_end)]
        optorderlist.append(end)
        origorder = ['Original order:   '] + org
        optorderlist.append(origorder)
        opt=['Optimized order:']+opt
        optorderlist.append(opt)
        dist1 = ['Original parts distance:'] + [origl]
        optorderlist.append(dist1)
        dist2 = ['Optimized parts distance:'] + [min]
        optorderlist.append(dist2)
        writeorderfile(optorderlist, optorderfile)

        i=i+1
        print 'Writing into file......'


    # input order file

    # orderfile = raw_input("Please list order file name: \n >")
    # readorder(orderfile)



    # for oneorder in optorderlist:
    # optorderlist.append(shortestpath(oneorder, x_init, y_init, x_end, y_end))

    # optorderfile = raw_input("Please list optimized order file name: \n >")
    # #test
    # a = [[1, 2, 3, 4], [2, 3, 234, 5, 643, 4, 4]]
    # writeorderfile(optorderlist, a)
    # dist = findpath(45, x_init, y_init)
    # readorder(optorderfile)
    print
    print


