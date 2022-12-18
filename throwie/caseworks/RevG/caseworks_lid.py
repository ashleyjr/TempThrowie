import Part
import math
from FreeCAD import Base

# Run in Freecad
# exec(open(<path_to_file>,'r').read())

# Parameters
base_length     = 58.5
base_width      = 23
base_depth      = 2

alcove_length   = 34
alcove_width    = 19
alcove_depth    = 4
alcove_length_offset   = 1.75
alcove_width_offset   = 2

recess_length   = 30
recess_width    = 15
recess_depth    = 4
recess_length_offset   = 3.75
recess_width_offset   = 4

batt_rad = 10
batt_depth = 4

batt_length_offset = 47
batt_width_offset = 11.5

cork_length   = 34
cork_width    = 5
cork_depth    = 8.5
cork_length_offset   = 1.75
cork_width_offset   = 16


# Name
name = "case_lid"

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

x = alcove_length_offset
y = (base_width - alcove_width) / 2
z = 0
alcove.translate(Base.Vector(x,y,z))

# Battery cut
batt = Part.makeCylinder(
    batt_rad,
    batt_depth)
batt.translate(Base.Vector(batt_length_offset,batt_width_offset,0))

# The alcove cut to fit the PCB
recess=Part.makeBox(
    recess_length,
    recess_width,
    recess_depth)
recess.translate(Base.Vector(recess_length_offset,recess_width_offset,0))

# The cork cut to queeze the PCB
cork=Part.makeBox(
    cork_length,
    cork_width,
    cork_depth)
cork.translate(Base.Vector(cork_length_offset,cork_width_offset,0))


Part.show(base)
alcove=alcove.cut(recess)
Part.show(alcove)
Part.show(batt)
Part.show(cork)


