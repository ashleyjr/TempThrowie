import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
top_length     = 38
top_width      = 32
top_depth      = 5

alcove_length   = 32
alcove_width    = 19
alcove_depth    = 5
alcove_offset   = 3

stantion_height   = 25
stantion_diameter = 5

# Name
name = "jig_top"

# Create new document
App.setActiveDocument(name)
App.closeDocument(name)
App.newDocument(name)
App.setActiveDocument(name)
App.ActiveDocument=App.getDocument(name)
Gui.ActiveDocument=Gui.getDocument(name)

# The major top
top=Part.makeBox(top_length,top_width,top_depth)

# The alcove cut to fit the PCB
alcove=Part.makeBox(
    alcove_length,
    alcove_width,
    alcove_depth)

x = alcove_offset
y = (top_width - alcove_width) / 2
z = top_depth
alcove.translate(Base.Vector(x,y,z))

Part.show(alcove)

stantion0=Part.makeCylinder(
    stantion_diameter,
    stantion_height)
top=top.cut(stantion0)

stantion1=stantion0.copy()
stantion1.translate(Base.Vector(top_length,0,0))
top=top.cut(stantion1)

stantion2=stantion0.copy()
stantion2.translate(Base.Vector(top_length,top_width,0))
top=top.cut(stantion2)

stantion3=stantion0.copy()
stantion3.translate(Base.Vector(0,top_width,0))
top=top.cut(stantion3)

Part.show(top)


