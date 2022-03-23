import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length     = 58.5
base_width      = 23
base_depth      = 9

alcove_length   = 34.5
alcove_width    = 19.5
alcove_depth    = 7.5
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

bot_length = 58.5
bot_depth = 2

wire_width = 10
wire_length = 2.5
wire_depth = base_depth
wire_width_offset = 6
wire_length_offset = 36
wire_depth_offset = 0

batt_rad = 10.5
batt_depth = base_depth
batt_width_offset = 11.5
batt_length_offset = 47

# Name
name = "case_bottom"

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
wire = Part.makeBox(wire_length,wire_width,wire_depth)
wire.translate(Base.Vector(wire_length_offset,wire_width_offset,wire_depth_offset))

# Battery cut
batt = Part.makeCylinder(
    batt_rad,
    batt_depth)
batt.translate(Base.Vector(batt_length_offset,batt_width_offset,0))


base=base.cut(alcove)
base=base.cut(ant)
base=base.cut(ldo)
base=base.cut(pwr)
base=base.cut(fet)
base=base.cut(wire)
base=base.cut(batt)
Part.show(base)

# Bot box
bot = Part.makeBox(bot_length,base_width,bot_depth)
bot.translate(Base.Vector(0,0,-bot_depth))
Part.show(bot)

