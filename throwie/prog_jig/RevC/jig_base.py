import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length     = 41
base_width      = 32
base_depth      = 15

alcove_length   = 34
alcove_width    = 19.5
alcove_depth    = 5
alcove_offset   = 3

ant_width   = 4
ant_length  = 8

ldo_width  = 13
ldo_length = 11

pwr_width  = 16.5
pwr_length = 12
pwr_offset  = 13

fet_width = 17
fet_length = 12
fet_offset = 1

stantion_height   = 20
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

# The major base
base=Part.makeBox(base_length,base_width,base_depth)

# The alcove cut to fit the PCB
alcove=Part.makeBox(
    alcove_length,
    alcove_width,
    alcove_depth)

x = alcove_offset
y = (base_width - alcove_width) / 2
z = (base_depth - alcove_depth)
alcove.translate(Base.Vector(x,y,z))

# Antenna cut
ant=Part.makeBox(alcove_offset+ant_length,ant_width,base_depth)
x = 0
y = (base_width - alcove_width) / 2
z = 0
ant.translate(Base.Vector(x,y,z))

# LDO cut
ldo = Part.makeBox(ldo_length,ldo_width,base_depth)
x = alcove_offset
y = (alcove_width - ldo_width) + ((base_width - alcove_width) / 2)
z =0
ldo.translate(Base.Vector(x,y,z))

# PWR cut
pwr = Part.makeBox(pwr_length,pwr_width,base_depth)
x = alcove_offset + pwr_offset
y = (alcove_width - pwr_width) + ((base_width - alcove_width) / 2)
z =0
pwr.translate(Base.Vector(x,y,z))

# PWR cut
fet = Part.makeBox(fet_length,fet_width,base_depth)
x = alcove_offset + alcove_length - fet_length
y = (fet_offset) + ((base_width - alcove_width) / 2)
z =0
fet.translate(Base.Vector(x,y,z))



base=base.cut(alcove)
base=base.cut(ant)
base=base.cut(ldo)
base=base.cut(pwr)
base=base.cut(fet)
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



