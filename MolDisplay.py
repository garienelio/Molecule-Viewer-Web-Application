import molecule
import html

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">""";

footer = """</svg>""";

defaultVal = """
  <radialGradient id="defaultVal" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
    <stop offset="0%" stop-color="#000000"/>
    <stop offset="50%" stop-color="#000000"/>
    <stop offset="100%" stop-color="#000000"/>
  </radialGradient>"""

offsetx = 500;
offsety = 500;

# Wrapper class for Atom
class Atom:
    # Constructor
    def __init__(self, atom):
        self.atom = atom
        self.z = atom.z

    # Str method for debugging
    def __str__(self):
        return ('%s, %lf, %lf, %lf' % (self.atom.element, self.atom.x, self.atom.y, self.atom.z,))
    
    # Generating svg file for atoms
    def svg(self):
        xCenter = (self.atom.x * 100.0) + offsetx
        yCenter = (self.atom.y * 100.0) + offsety
        # atomRadius = radius[self.atom.element]
        # atomColor = html.escape(element_name[self.atom.element])

        if self.atom.element in element_name:
            atomRadius = radius[self.atom.element]
            atomColor = html.escape(element_name[self.atom.element])
        else:
            atomRadius = 35
            atomColor = "defaultVal"


        return ('  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (xCenter, yCenter, atomRadius, atomColor))

# Wrapper class for Bond
class Bond:
    # Constructor
    def __init__(self, bond):
        self.bond = bond
        self.z = bond.z
    
    # Str method for debugging
    def __str__(self):
        x1 = self.bond.x1
        x2 = self.bond.x2
        y1 = self.bond.y1
        y2 = self.bond.y2
        z = self.bond.z
        bondLen = self.bond.len
        dx = self.bond.dx
        dy = self.bond.dy

        return ('x1: %lf, y1: %lf, x2: %lf, y2: %lf, z: %lf, len: %lf, dx: %lf, dy: %lf' % (x1, y1, x2, y2, z, bondLen, dx, dy,))

    # Generating svg file for bonds
    def svg(self):
        # Calculating the coordinate points for the bonds
        x11 = ((self.bond.x1 * 100.0) + offsetx) + (self.bond.dy * 10)
        y11 = ((self.bond.y1 * 100.0) + offsety) - (self.bond.dx * 10)

        x12 = ((self.bond.x1 * 100.0) + offsetx) - (self.bond.dy * 10)
        y12 = ((self.bond.y1 * 100.0) + offsety) + (self.bond.dx * 10)

        x21 = ((self.bond.x2 * 100.0) + offsetx) - (self.bond.dy * 10)
        y21 = ((self.bond.y2 * 100.0) + offsety) + (self.bond.dx * 10)

        x22 = ((self.bond.x2 * 100.0) + offsetx) + (self.bond.dy * 10)
        y22 = ((self.bond.y2 * 100.0) + offsety) - (self.bond.dx * 10)

        return ('  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x11, y11, x12, y12, x21, y21, x22, y22,))

# Wrapper class for molecule
class Molecule(molecule.molecule):
    # Str method for debugging
    def __str__(self):
        for i in self.atoms:
            print(i)

        for i in self.bonds:
            print(i)

    # Generating the svg file for the molecule
    def svg(self):
        svgString = header + '\n'

        svgString += defaultVal

        i = j = 0
        while i < self.atom_no and j < self.bond_no:
            a = Atom(self.get_atom(i))
            b = Bond(self.get_bond(j))
            if a.z < b.z:
                svgString += a.svg()
                i += 1
            else:
                svgString += b.svg()
                j += 1
    
        while i < self.atom_no:
            a = Atom(self.get_atom(i))
            svgString += a.svg()
            i += 1

        while j < self.bond_no:
            b = Bond(self.get_atom(j))
            svgString += b.svg()
            j += 1
        
        svgString += footer

        return svgString

    # Parsing the input (.sdf file)
    def parse(self, file):

        # Read the total number of atoms and bonds
        for i in range(3):
            lineContent = file.readline()
        lineContent = file.readline()

        lineList = lineContent.split(' ')
        lineList = [i for i in lineList if i != '']

        totalAtom = int(lineList[0])
        totalBond = int(lineList[1])

        # Parsing all the atoms data inside the .sdf file
        for i in range(totalAtom):
            lineContent = file.readline()
            lineList = lineContent.split(' ')
            lineList = [j for j in lineList if j != '']
            self.append_atom(lineList[3], float(lineList[0]), float(lineList[1]), float(lineList[2]))

        # Parsing all the bonds data inside the .sdf file
        for i in range(totalBond):
            lineContent = file.readline()
            lineList = lineContent.split(' ')
            lineList = [j for j in lineList if j != '']
            self.append_bond(int(lineList[0]) - 1, int(lineList[1]) - 1, int(lineList[2]))
