import Part
import math
from FreeCAD import Base

name = "throwie"

#Create new document
try:
    App.setActiveDocument(name)
except Exception as e:
    print(e)
try:
    App.closeDocument(name)
except Exception as e:
    print(e)
App.newDocument(name)
App.setActiveDocument(name)
App.ActiveDocument=App.getDocument(name)
Gui.ActiveDocument=Gui.getDocument(name)


height_mm = 25
width_mm = 24
depth_mm = 10

b=Part.makeBox(height_mm,width_mm,depth_mm)
Part.show(b)

