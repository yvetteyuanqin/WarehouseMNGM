__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse application"

import csv
import sys
import graphtest
import networkx as nx

loc_dict = {}  # location according to id
orderlist = [];
optorderlist = [];
pathnode = nx.Graph()

# readin products location
def readin():
    # rack = []
    # with open('warehouse-grid.csv') as csvfile:
    #     spamreader = csv.reader(csvfile)
    #     for row in spamreader:
    #         row[0] = int(row[0])
    #         row[1] = round(float(row[1])) * 2
    #         row[2] = round(float(row[1])) * 2
    #
    #         rack.append(row)
    # # for stuff in rack:
    # #     print(stuff)
    # print "total goods num:", len(rack)


    with open('warehouse-grid.csv') as csvfile:
        spamreader = csv.reader(csvfile)
        max_x = 0
        max_y = 0
        for row in spamreader:
            pro_id = int(row[0])
            pro_x = int(float(row[1])) * 2+1 #double the cordinates to simulate the path and move the rack from(0,0)to (1,1)
            pro_y = int(float(row[2])) * 2+1
            if pro_x>max_x:
                max_x = pro_x
            if pro_y>max_y:
                max_y = pro_y
            loc_dict[pro_id] = [pro_x, pro_y]
    print "total goods num:", len(loc_dict)
    max_x = (max_x-1)/2
    max_y = (max_y - 1) / 2
    print "max rack number in row, col", max_x, max_y

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
        print orderlist

# find shortest path between two points
def findpath(pro_id,init_x = 0, init_y = 0):
    pro_id = int(pro_id)
    if pro_id not in loc_dict:
        print "id not exist"
        return -1

    pro_x = loc_dict[pro_id][0]     #x,y coordinates of products
    pro_y = loc_dict[pro_id][1]
    print "Searching product id",pro_id, "product position", (pro_x,pro_y)
    print "Calculating shortest path for one item......"

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
    print "desired position",  (des_x,des_y)
    # algorithm:x+y
    # if init_x==0 and init_y ==0 or init_y % 2 == 0:
    #     print "first x dir than y dir:", (init_x,init_y),"to",(des_x,init_y),"to",(des_x,des_y)
    #     distance = abs(des_x - init_x) + abs(des_y - init_y)
    # else:
    #     # rack in the way, 1 move in y direction first, update initial y
    #     print"rack in the way",(init_x,init_y),"to", (init_x,init_y+1)
    #     init_y = init_y+1
    #     print "first x dir than y dir:", (init_x,init_y),"to",(des_x,init_y),"to",(des_x,des_y)
    #     distance = abs(des_x - init_x) + abs(des_y - init_y)+1

    # route and distance print in pathgraph()
    # algorithm: creating path graph and use dijkstra
    itemdistance = graphtest.pathgraph(des_x, des_y,init_x,init_y)
    return itemdistance, des_x, des_y




#!!!!!!!!!!!!!!!!!!
def optimizeorder(oneorder):
    optoneorder = []
    orderloc = []
    for item_no in oneorder:
        orderloc.append(loc_dict[item_no])

    print "compute TSP"
    #findpath()
    return optoneorder



def writeorderfile(a,s):
    with open(s, "w+") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter='\t')
        csvWriter.writerows(a)

def singleOrder():

    orderlist = raw_input("Hello User, what items would you like to pick?: ")
    spamorderlist = orderlist.split(',')
    oneorder = []
    # (x_init,y_init)= input("Hello User, where is your worker? (x,y):  default(0,0) \n > ")
    1 # (x_end, y_end) = input("What is your worker's end location? (x,y):   default(0,20) \n > ")
    for element in spamorderlist:
        oneorder.append(int(element))
    print 'the order ready to pick: ',oneorder

    # # original order
    # x_init = 0
    # y_init = 0
    # dist_oneorder = 0
    # for item in oneorder:
    #     dist, x_des, y_des= findpath(item,x_init,y_init)
    #     x_init = x_des
    #     y_init = y_des
    #     dist_oneorder = dist_oneorder + dist
    #     print
    # # back to end point
    #
    # print"returning to end point......"
    # backtrip = graphtest.pathgraph(0, 20, x_init, y_init)
    # dist_oneorder = dist_oneorder + backtrip
    #
    # print 'Distance for one order without optimization', dist_oneorder

    optimizeorder(oneorder)



if __name__ == '__main__':
    print
    print

    readin()

    # input single order
    singleOrder()

    # compute shortest path

    x_end = 0
    y_end = 20
    x_init = 0
    y_init = 0
    # optoneorder = shortestpath(oneorder, x_init, y_init, x_end, y_end)

    # input order file

    # orderfile = raw_input("Please list order file name: \n >")
    # readorder(orderfile)

    # compute shortest path
    # (x_end, y_end) = input("What is your worker's end location? (x,y):   default(0,10) \n > ")
    # (x_init,y_init)= input("Hello User, where is your worker? (x,y):  default(0,0) \n > ")
    # x_end = 0
    # y_end = 20
    # x_init = 0
    # y_init = 0

    # for oneorder in optorderlist:
    #     optorderlist.append(shortestpath(oneorder, x_init, y_init, x_end, y_end))

    # optorderfile = raw_input("Please list optimized order file name: \n >")
    # #test
    # a = [[1, 2, 3, 4], [2, 3, 234, 5, 643, 4, 4]]
    # writeorderfile(optorderlist, a)
    # dist = findpath(45, x_init, y_init)
    # readorder(optorderfile)
    print
    print


