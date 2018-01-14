import sys
import math
import pylab as plt
import numpy as np
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication


def binomial(i, n):
    """Binomial coefficient"""
    return math.factorial(n) / float(
        math.factorial(i) * math.factorial(n - i))


def bernstein(t, i, n):
    """Bernstein polynom"""
    return binomial(i, n) * (t ** i) * ((1 - t) ** (n - i))


def bezier(t, points):
    """Calculate coordinate of a point in the bezier curve"""
    n = len(points) - 1
    x = y = 0
    for i, pos in enumerate(points):
        bern = bernstein(t, i, n)
        x += pos[0] * bern
        y += pos[1] * bern
    return x, y


def bezier_curve_range(n, points):
    """Range of points in a curve bezier"""
    res=[]
    for i in range(n):
        t = i / float(n - 1)
        res.append(bezier(t, points))
    return np.array(res)
        
        
        
class LUT(QtGui.QWidget):

    def __init__(self):
        super(LUT, self).__init__()
        self.initUI()
    
    def initUI(self):      
    
        self.setGeometry(0, 0, 255, 255)
        self.setWindowTitle('Draw LUT')
        self.show()
        #matrix :  #points * (bef,main,aft) * (x,y)
        self.bezierCoord = np.array([[[15,15],[15,15],[15,15]], [[100,100],[150,100],[150,120]], [[250,250],[250,250],[250,250]]], dtype=np.float)
        self.movepoint=False
        
    def getBezierCurveCoord(self):
        points = np.reshape(self.bezierCoord,(int(self.bezierCoord.size/2),2))[1:-1]
        a=[]
        for i in np.arange(self.bezierCoord.shape[0]-1):
            a.append(bezier_curve_range(300,points[(i*3):(i*3+4)]))
        a = np.array(a)
        return np.reshape(a,(int(a.size/2),2))
        
    def drawBezierPoint(self,qp,i):
        a,b,c = self.bezierCoord[i,:,:]
        start = QtCore.QPointF(a[0],a[1])
        main = QtCore.QPointF(b[0],b[1])
        end = QtCore.QPointF(c[0],c[1])
        
        # draw first point
        pen = QtGui.QPen(QtGui.QColor("#000000"), 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        qp.setBrush(brush)
        qp.drawEllipse(main,5,5)
        
        # draw bezier arms points
        brush = QtGui.QBrush(QtCore.Qt.NoBrush)
        qp.setBrush(brush)
        qp.drawEllipse(start,4,4)
        qp.drawEllipse(end,4,4)
        
        # draw bezier arms
        pen = QtGui.QPen(QtGui.QColor("#555555"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(start,main)
        qp.drawLine(main,end)
        
    def drawBezierCurve(self, qp):
        # Set the Bezier curve
        self.bezierCurve = QtGui.QPainterPath(QtCore.QPointF(self.bezierCoord[0,1,0],self.bezierCoord[0,1,1]))
        for i in np.arange(1,len(self.bezierCoord)):
            self.bezierCurve.cubicTo(QtCore.QPointF(self.bezierCoord[i-1,2,0],self.bezierCoord[i-1,2,1]), 
                                QtCore.QPointF(self.bezierCoord[i,0,0],self.bezierCoord[i,0,1]),
                                QtCore.QPointF(self.bezierCoord[i,1,0],self.bezierCoord[i,1,1]))  
        # draw the Bezier curve
        pen = QtGui.QPen(QtGui.QColor("#333333"), 3, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawPath(self.bezierCurve)
        pen = QtGui.QPen(QtGui.QColor("#000000"), 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        
    def drawBezierAll(self, qp):
        self.drawBezierCurve(qp)
        for i in np.arange(len(self.bezierCoord)):
            self.drawBezierPoint(qp,i)
        
    def paintEvent(self, e):
        x,y,sx,sy = self.geometry().getRect()
        self.bezierCoord[:,:,0] -= self.bezierCoord[0,1,0]
        self.bezierCoord[:,:,1] -= self.bezierCoord[0,1,1]
        self.bezierCoord[:,:,0] = self.bezierCoord[:,:,0] / self.bezierCoord[-1,1,0]
        self.bezierCoord[:,:,1] = self.bezierCoord[:,:,1]  / self.bezierCoord[-1,1,1]
        self.bezierCoord[:,:,0] *= sx
        self.bezierCoord[:,:,1] *= sy
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawBezierAll(qp)
        qp.end()
    
    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            x = event.x()
            y = event.y()
            mat = (self.bezierCoord[:,:,0] - x)**2 + (self.bezierCoord[:,:,1] - y)**2
            if np.min(mat)<100:
                argmini = np.argmin(mat)
                imain = argmini // 3
                ipoint = argmini % 3
                self.movepoint=True
                self.selectedpoint=(imain,ipoint)
        if event.button() == QtCore.Qt.RightButton:
            print("lol") # add a new button or remove one if the click is close to one

    def mouseMoveEvent(self,event):
        if self.movepoint==True:
            x = event.x()
            y = event.y()
            if self.selectedpoint[1] == 1:
                diff = self.bezierCoord[self.selectedpoint[0],1,:] - [x,y]
                self.bezierCoord[self.selectedpoint[0],:,:] -= [diff,diff,diff]
                
            else:
                self.bezierCoord[self.selectedpoint[0],self.selectedpoint[1],:] = x,y
            self.update()
            
    def mouseReleaseEvent(self,event):
        self.movepoint=False
        
        
try:
    app
except:
    app=QApplication([])
view = LUT()
view.setGeometry(100, 100, 1600, 900)
view.setWindowTitle('MainWindow')
view.show()
app.exec_()