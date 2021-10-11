import Part
import math
from FreeCAD import Base

name = "pcb"

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

height_mm = 22.4
width_mm = 14.5
depth_mm = 0.6

b=Part.makeBox(height_mm,width_mm,depth_mm)

Part.show(b)
