import Part
import math
from FreeCAD import Base

name = "battery"

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

rad_mm = 10
dph_mm = 3

b=Part.makeCylinder(rad_mm,dph_mm)

Part.show(b)

