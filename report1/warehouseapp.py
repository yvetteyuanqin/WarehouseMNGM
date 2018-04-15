__author__ = 'Yuan Qin'
__date__ = "4/5/2018"
__projectname__ = "warehouse"

import csv
import sys
loc_dict = {}  # location according to id

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



def findpath(pro_id,init_x = 0, init_y = 0):
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



if __name__ == '__main__':
    print
    print
    readin()

    if len(sys.argv) == 2:
        print "Product id:", sys.argv[1], ", with initial position(0,0)"
        findpath(sys.argv[1])
    elif len(sys.argv) == 4:
        print "Product id:", sys.argv[1], ", with initial position (", int(sys.argv[2]), ",", int(sys.argv[3]), ")"
        findpath(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    else:
        print sys.argv[0],"input argv #:", len(sys.argv)," Please enter the product id in the command line, initial position default as(0,0) if no input specified"

    print
    print

