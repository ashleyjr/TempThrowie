import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length       = 37.5
base_width        = 40
base_depth        = 5
stantion_diameter = 6

# Name
name = "jgg_top"

# Create new document
if len(App.listDocuments()) != 0:
    for doc in App.listDocuments():
        App.setActiveDocument(doc)
        App.closeDocument(doc)
App.newDocument(name)
App.setActiveDocument(name)
App.ActiveDocument=App.getDocument(name)
Gui.ActiveDocument=Gui.getDocument(name)

# The major base
base=Part.makeBox(base_length,base_width,base_depth)

# Stantion cuts
stantion0=Part.makeCylinder(
    stantion_diameter,
    base_depth)
stantion1=stantion0.copy()
stantion1.translate(Base.Vector(base_length,0,0))
stantion2=stantion0.copy()
stantion2.translate(Base.Vector(base_length,base_width,0))
stantion3=stantion0.copy()
stantion3.translate(Base.Vector(0,base_width,0))

base=base.cut(stantion0)
base=base.cut(stantion1)
base=base.cut(stantion2)
base=base.cut(stantion3)
Part.show(base)



