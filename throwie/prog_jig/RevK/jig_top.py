import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length       = 37.5
base_width        = 40
base_depth        = 5
stantion_diameter = 5.4
probe_radius      = 0.75
probe_num         = 2
probe_positions   = [
    [3.6,   26.9],
    [3.6,   24.4],
    [4.1,   15],
    [6.7,   26.9],
    [9.7,   26.9],
    [12.7,  26.9],
    [14.8,  16.9],
    [14.8,  13.9],
    [33,    25.3],
        ]
wedge_length = 10
wedge_width = 4
wedge_depth = 6
wedge_x = 22
wedge_y = 12
wedge_z = -wedge_depth

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

# The wedge
wedge=Part.makeBox(wedge_length,wedge_width,wedge_depth)
wedge.translate(Base.Vector(wedge_x,wedge_y,wedge_z))

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
stantion4=stantion0.copy()
stantion4.translate(Base.Vector(base_length/2,0,0))
base=base.cut(stantion0)
base=base.cut(stantion1)
base=base.cut(stantion2)
base=base.cut(stantion3)
base=base.cut(stantion4)

# Probe cuts
probe=Part.makeCylinder(
    probe_radius,
    base_depth)

probes = []
for pos in probe_positions:
    x = probe.copy()
    x.translate(Base.Vector(pos[0],pos[1],0))
    base=base.cut(x)

Part.show(wedge)
Part.show(base)


