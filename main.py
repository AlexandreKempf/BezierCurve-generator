import sys
import math
import pylab as plt
import numpy as np
from PyQt5 import QtCore
from PyQt5 import QApplication

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

app=QApplication([])
a = QtGui.QWidget()
a.bezierCoord = np.array([[[0,0],[0,0],[0,0]], [[0.5,0.5],[0.5,0.5],[0.5,0.5]], [[1,1],[1,1],[1,1]]], dtype=np.float)
a.setGeometry(100, 100, 800, 500)
a.setWindowTitle('MainWindow')
a.show()



app.exec_()
