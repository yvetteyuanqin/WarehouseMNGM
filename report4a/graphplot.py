import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.path import Path
import matplotlib.patches as patches
import networkx as nx
import numpy as np
from warehouseapp import *
from graphtest import locdistance


pathgraph = nx.Graph()

class App(QWidget):
    NumButtons = ['Clear', 'Routing', 'not_implemented']
    NumTextBox = ['initial','end','']
    def __init__(self):
        super(App,self).__init__()
        self.title = 'Warehouse Management Syetem'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    #     order info
        self.max_x = 20
        self.max_y = 10
        self.x_init = None
        self.y_init = None
        self.x_end = None
        self.y_end = None
        self.oneorder = []

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #button
        grid = QGridLayout()
        self.setLayout(grid)
        self.createVerticalGroupBox()
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.verticalGroupBox)
        grid.addLayout(buttonLayout, 5,0)
        #plot
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        grid.addWidget(self.canvas, 0, 1, 9, 9)
        # input initial and end position
        self.textbox1 = QLineEdit(self)
        self.textbox1.move(20, 20)
        self.textbox1.resize(100, 30)
        self.textbox2 = QLineEdit(self)
        self.textbox2.move(20, 90)
        self.textbox2.resize(100, 30)
        self.textbox3 = QLineEdit(self)
        self.textbox3.move(20, 160)
        self.textbox3.resize(100, 30)

        # Create a button in the window
        self.button1 = QPushButton('Set initial', self)
        self.button1.move(20, 50)
        self.button2 = QPushButton('Set end', self)
        self.button2.move(20, 120)
        self.button3 = QPushButton('One order', self)
        self.button3.move(20, 190)
        # connect button to function on_click
        self.button1.clicked.connect(self.on_click1)
        self.button2.clicked.connect(self.on_click2)
        self.button3.clicked.connect(self.enterorder_click)
        self.show()

    # onclick 1 2 set initial and end position
    def on_click1(self):
        x_init,y_init= self.textbox1.text().split(',')
        self.x_init=int(x_init)
        self.y_init = int(y_init)
        print('initial x: ',self.x_init,', y: ',self.y_init )
    def on_click2(self):
        x_end,y_end= self.textbox2.text().split(',')
        self.x_end = int(x_end)
        self.y_end = int(y_end)
        print('end point x: ',self.x_end,', y: ',self.y_end )
    def enterorder_click(self):
        self.oneorder = self.textbox3.text().split('\t')
        print('one order entered:', self.oneorder)


    def createVerticalGroupBox(self):
        self.verticalGroupBox = QGroupBox()

        layout = QVBoxLayout()
        for i in self.NumButtons:
            button = QPushButton(i)
            button.setObjectName(i)
            layout.addWidget(button)
            layout.setSpacing(10)
            self.verticalGroupBox.setLayout(layout)
            button.clicked.connect(self.submitCommand)

    def submitCommand(self):
        eval('self.' + str(self.sender().objectName()) + '()')

    def Clear(self):#rack position
        self.figure.clf()
        ax1 = self.figure.add_subplot(111)
        for i in range(1,40,2):
            y = [e for e in range(1,20,2)]
            ax1.plot(i*np.ones(len(y)), y, 's',markersize=4)
        axes1 = plt.gca()
        axes1.set_ylim([-1, 21])
        axes1.set_xlim([-1, 41])
        ax1.set_title('Rack Position')
        self.canvas.draw_idle()

    def Routing(self):#

        ax2 = self.figure.add_subplot(111)
        axes2 = plt.gca()
        axes2.set_ylim([-1, 21])
        axes2.set_xlim([-1,41])
        ax2.set_title('Routing')
        #process one order
        if self.oneorder==[] or self.x_init==None or self.y_init==None or self.x_end==None or self.y_init==None:
            self.x_init = 0
            self.y_init = 0
            self.x_end = 0
            self.y_end = 20
            self.oneorder = [1,45,74]
        x_temp=self.x_init
        y_temp=self.y_init
        oneorder=[]
        for elem in self.oneorder:
            oneorder.append(int(elem))

        org, origl, opt, min=singleOrder(pathgraph,oneorder,self.x_init,self.y_init,self.x_end,self.y_init)
        print (org,opt)
        for item in opt:
            if item not in loc_dict:
                print("id not exist")
                return -1

            pro_x = loc_dict[item][0]  # x,y coordinates of products
            pro_y = loc_dict[item][1]
            if self.x_init < pro_x:
                des_x = pro_x - 1  # shorter to take from left path of the rack
                des_y = pro_y
                # if pro_x == 0:
                #     des_x = pro_x + 1 #can only take from right since its the boundary, say wall
                #     des_y = pro_y
            # if the product position is west to the current position i.e. init_x > prod_x
            elif self.x_init > pro_x:
                des_x = pro_x + 1  # shorter to take from right path of the rack
                des_y = pro_y
                # if pro_x == 20:
                #     des_x = pro_x - 1 #can only take from left since its the boundary, say wall
                #     des_y = pro_y
            else:
                des_x = self.x_init
                des_y = pro_y
            min,traversedpoint=locdistance(pathgraph,des_x,des_y,self.x_init,self.y_init)
            data = np.array(traversedpoint)
            plt.plot(data[:, 0], data[:, 1])
            self.x_init=des_x
            self.y_init=des_y
        min, traversedpoint = locdistance(pathgraph, self.x_end, self.y_end, self.x_init, self.y_init)#to end point
        data = np.array(traversedpoint)
        plt.plot(data[:, 0], data[:, 1])
        self.x_init = x_temp
        self.y_init = y_temp

        #draw order path


        self.canvas.draw_idle()

    def not_implemented(self):
        self.figure.clf()
        ax3 =self.figure.add_subplot(111)
        ax3.set_title('trypath')
        data = np.array([[1, 2], [2, 4], [3, 5], [4, 5]])
        plt.plot(data[:, 0], data[:, 1])


        # B = nx.Graph()
        # B.add_nodes_from([1, 2, 3, 4], bipartite=0)
        # B.add_nodes_from(['a', 'b', 'c', 'd', 'e'], bipartite=1)
        # B.add_edges_from([(1, 'a'), (2, 'c'), (3, 'd'), (3, 'e'), (4, 'e'), (4, 'd')])
        #
        # X = set(n for n, d in B.nodes(data=True) if d['bipartite'] == 0)
        # Y = set(B) - X
        #
        # X = sorted(X, reverse=True)
        # Y = sorted(Y, reverse=True)
        #
        # pos = dict()
        # pos.update((n, (1, i)) for i, n in enumerate(X))  # put nodes from X at x=1
        # pos.update((n, (2, i)) for i, n in enumerate(Y))  # put nodes from Y at x=2
        # nx.draw(B, pos=pos, with_labels=True)
        self.canvas.draw_idle()


if __name__ == '__main__':

    readin()



    pathgraph = createpathg(max_x, max_y, 2, 1)





    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

