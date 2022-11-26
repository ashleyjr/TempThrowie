import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length     = 37.5
base_width      = 40
base_depth      = 12

alcove_length   = 34.5
alcove_width    = 19.5
alcove_depth    = 10
alcove_offset   = 1.5

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

stantion_height   = 30
stantion_diameter = 5

wire_length = 6
wire_depth = 10
wire_offset = 19

wind_width = 16
wind_depth = 10
wind_x = 0
wind_y = 12
wind_z = 5 


# Name
name = "jig_base"

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

# FET cut
fet = Part.makeBox(fet_length,fet_width,base_depth)
x = alcove_offset + alcove_length - fet_length
y = (fet_offset) + ((base_width - alcove_width) / 2)
z =0
fet.translate(Base.Vector(x,y,z))

# Wire cut
wire=Part.makeBox(wire_length,(base_width-alcove_width)/2,wire_depth)
wire.translate(Base.Vector(wire_offset,(alcove_width+((base_width-alcove_width)/2)),0))

# Window cut
wind=Part.makeBox(base_length,wind_width,wind_depth)
wind.translate(Base.Vector(wind_x,wind_y,wind_z))

base=base.cut(alcove)
base=base.cut(ant)
base=base.cut(ldo)
base=base.cut(pwr)
base=base.cut(fet)
base=base.cut(wire)
base=base.cut(wind)
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

stantion4=stantion0.copy()
stantion4.translate(Base.Vector(base_length/2,0,0))
Part.show(stantion4)


