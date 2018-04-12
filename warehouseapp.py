__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse application"

import csv
import sys
loc_dict = {}  # location according to id
orderlist = [];
optorderlist = [];

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
        for row in spamreader:
            pro_id = int(row[0])
            pro_x = int(int(float(row[1])) * 2)+1 #double the cordinates to simulate the path and move the rack from(0,0)to (1,1)
            pro_y = int(int(float(row[2])) * 2)+1 #then the robot only operate on coordinate with even number

            loc_dict[pro_id] = [pro_x, pro_y]
    print "total goods num:", len(loc_dict)

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

#!!!!!!!!!!!!!!!!!!!
def findpath(pro_id,init_x = 0, init_y = 0, end_x = 0, end_y = 20):
    pro_id = int(pro_id)
    if pro_id not in loc_dict:
        print "id not exist"
        return -1

    pro_x = loc_dict[pro_id][0]     #x,y coordinates of products
    pro_y = loc_dict[pro_id][1]
    print "Searching product #", pro_id, "product position", (pro_x,pro_y)
    print "Calculating shortest path ......"
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

    if init_x==0 and init_y ==0 or init_y % 2 == 0:
        print "first x dir than y dir:", (init_x,init_y),"to",(des_x,init_y),"to",(des_x,des_y)
        distance = abs(des_x - init_x) + abs(des_y - init_y)
    else:
        # rack in the way, 1 move in y direction first, update initial y
        print"rack in the way",(init_x,init_y),"to", (init_x,init_y+1)
        init_y = init_y+1
        print "first x dir than y dir:", (init_x,init_y),"to",(des_x,init_y),"to",(des_x,des_y)
        distance = abs(des_x - init_x) + abs(des_y - init_y)+1


    print "Total distance is : ", distance

#!!!!!!!!!!!!!!!!!!
def shortestpath(oneorder):
    optoneorder = []
    ordersloc = []
    for item_no in oneorder:
        ordersloc.append(loc_dict[item_no])
    return



def writeorderfile(a,s):
    with open(s, "w+") as my_csv:
        csvWriter = csv.writer(my_csv, delimiter='\t')
        csvWriter.writerows(a)


if __name__ == '__main__':
    print
    print

    #readin()

    #input

    orderlist = raw_input("Hello User, what items would you like to pick?: ")
    spamorderlist = orderlist.split(',')
    oneorder = []
    for element in spamorderlist:
        oneorder.append(int(element))
    optoneorder = shortestpath(oneorder)

    # (x_init,y_init)= input("Hello User, where is your worker? (x,y):  default(0,0) \n > ")
    # (x_end, y_end) = input("What is your worker's end location? (x,y):   default(0,10) \n > ")
    # orderfile = raw_input("Please list order file name: \n >")
    # readorder(orderfile)
    # for oneorder in orderlist:
    #     optorderlist.append(shortestpath(oneorder))

    # optorderfile = raw_input("Please list optimized order file name: \n >")
    # #test
    # a = [[1, 2, 3, 4], [2, 3, 234, 5, 643, 4, 4]]
    # writeorderfile(optorderlist, a)
    # # findpath(pro_id, x_init, y_init, x_end, y_end)
    # readorder(optorderfile)
    print
    print


