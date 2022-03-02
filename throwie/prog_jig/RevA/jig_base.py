import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length     = 70
base_width      = 50
base_depth      = 20

alcove_length   = 50
alcove_width    = 30
alcove_depth    = 10

shelf_width     = 2
shelf_depth     = 5

stantion_height   = 40
stantion_diameter = 5

# Name
name = "jig_base"

# Create new document
App.setActiveDocument(name)
App.closeDocument(name)
App.newDocument(name)
App.setActiveDocument(name)
App.ActiveDocument=App.getDocument(name)
Gui.ActiveDocument=Gui.getDocument(name)

# Cut shelf out the alcove, cut alcove out of base
base=Part.makeBox(base_length,base_width,base_depth)

shelf=Part.makeBox(
    alcove_length-shelf_width,
    alcove_width-(2*shelf_width),
    shelf_depth)

x = 0
y = (base_width - alcove_width + (2*shelf_width)) / 2
z = (base_depth - alcove_depth)
shelf.translate(Base.Vector(x,y,z))

alcove=Part.makeBox(
    alcove_length,
    alcove_width,
    alcove_depth-shelf_depth)

x = 0
y = (base_width - alcove_width) / 2
z = (base_depth - alcove_depth + shelf_depth)
alcove.translate(Base.Vector(x,y,z))

base=base.cut(shelf)
base=base.cut(alcove)
Part.show(base)

stantion0=Part.makeCylinder(
    stantion_diameter,
    stantion_height)
Part.show(stantion0)

stantion1=stantion0.copy()
stantion1.translate(Base.Vector(base_length,0,0))
Part.show(stantion1)

stantion2=stantion0.copy()
stantion2.translate(Base.Vector(base_length,base_width,0))
Part.show(stantion2)

stantion3=stantion0.copy()
stantion3.translate(Base.Vector(0,base_width,0))
Part.show(stantion3)



