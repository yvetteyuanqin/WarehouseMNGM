import networkx as nx

import matplotlib.pyplot as plt

import numpy as np
# pathgraph.add_node(0,coordinate=[1,2])
# print pathgraph.node[0]['coordinate']

max_x=18
max_y=10
d=2 #distance between nodes along rack width
l=1 #rack

def pathgraph(des_x=0,des_y=20,init_x=0,init_y=0):
    i=0
    pathgraph = nx.Graph()
    # create graph
    # add nodes
    for c in range(2*max_x+1):
        if c % 2 ==0:
            for r in range(2*max_y+1):
                pathgraph.add_node(i,coordinate=[c,r])
                i=i+1
                # print [c,r]
    # print pathgraph.nodes
    # add edges
    # vertical edges
    for c in range(max_x):
        for i in range(max_y*2):
            pathgraph.add_edge(c * (2 * max_y + 1)+i, c * (2 * max_y + 1) +i+ 1, distance=1)
    # horizontal edges
    for r in range(0,2*max_y+1,2):
        for c in range(max_x):
            pathgraph.add_edge(c*(2*max_y+1)+r, (c+1)*(2*max_y+1)+ r, distance=2)
    # print pathgraph.edges

    # pos = nx.spring_layout(pathgraph)
    # nx.draw(pathgraph, pos)

    # look for the key number of node according to location given
    # pgone = pathgraph.subgraph([i for i, node in pathgraph.nodes(data=True) if node['coordinate'] == [init_x, init_y]])
    # positioninit = int(list(pgone.node)[0])
    # quicker
    positioninit = init_x/2*(2*max_y+1)+init_y
    positiondes = des_x / 2 * (2 * max_y + 1) + des_y

    # print 'position node of original: ', positioninit  # node number with attr of(init_x,init_y)

    # pgone = pathgraph.subgraph([i for i, node in pathgraph.nodes(data=True) if node['coordinate'] == [des_x, des_y]])
    # positiondes = int(list(pgone.node)[0])
    # print 'position node of destination: ',positiondes  # node number with attr of(des_x,des_y)

    # compute shortest path and distance
    traversednodelist = list(nx.dijkstra_path(pathgraph, positioninit, positiondes, 'distance'))

    traversedpoint = []
    for node in traversednodelist:
        coordinates = nx.get_node_attributes(pathgraph, 'coordinate')
        traversedpoint.append(coordinates[node])

    # print out path
    # print 'Traverse node: ', nx.dijkstra_path(pathgraph, positioninit, positiondes, 'distance')
    # print 'According coordinate:', traversedpoint
    # print 'with distance for one item:', nx.dijkstra_path_length(pathgraph, positioninit, positiondes, 'distance')

    itemdistance = nx.dijkstra_path_length(pathgraph, positioninit, positiondes, 'distance')
    return itemdistance
    # distance = nx.get_edge_attributes(pathgraph, 'distance')
    # print distance[(0, 21)]
    # print list(pathgraph.edges)[0][1]






if __name__ == '__main__':

    print
    print

    itemdist = pathgraph()
    # print 'total node number: ',nodenumber
    # SG = G.subgraph([n for n, attrdict in G.node.items() if attrdict['type'] == 'X'])

