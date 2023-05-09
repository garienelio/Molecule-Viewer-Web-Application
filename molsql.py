import os
import sqlite3
import MolDisplay
import html

radialGradientSVG = """
  <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
    <stop offset="0%%" stop-color="#%s"/>
    <stop offset="50%%" stop-color="#%s"/>
    <stop offset="100%%" stop-color="#%s"/>
  </radialGradient>"""

class Database:
    def __init__(self, reset=False):
        # Remove old database if reset is true
        if (reset == True) and (os.path.exists('molecules.db')):
            os.remove('molecules.db')
        
        # Establish connection to the database
        self.conn = sqlite3.connect("molecules.db")
    

    # Creating tables to the database
    def create_tables(self):
        # Creating Elements table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Elements
                             (ELEMENT_NO    INTEGER      NOT NULL,
                             ELEMENT_CODE  VARCHAR(3)   NOT NULL,
                             ELEMENT_NAME  VARCHAR(32)  NOT NULL,
                             COLOUR1       CHAR(6)      NOT NULL,
                             COLOUR2       CHAR(6)      NOT NULL,
                             COLOUR3       CHAR(6)      NOT NULL,
                             RADIUS        DECIMAL(3)   NOT NULL,
                             PRIMARY KEY (ELEMENT_CODE));""")

        # Creating Atoms table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Atoms
                             (ATOM_ID       INTEGER       PRIMARY KEY  AUTOINCREMENT  NOT NULL,
                             ELEMENT_CODE  VARCHAR(3)    NOT NULL,
                             X             DECIMAL(7,4)  NOT NULL,
                             Y             DECIMAL(7,4)  NOT NULL,
                             Z             DECIMAL(7,4)  NOT NULL,
                             FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE));""")

        # Creating Bonds table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Bonds
                             (BOND_ID  INTEGER  PRIMARY KEY  AUTOINCREMENT  NOT NULL,
                             A1       INTEGER  NOT NULL,
                             A2       INTEGER  NOT NULL,
                             EPAIRS   INTEGER  NOT NULL);""")

        # Creating Molecules table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS Molecules
                             (MOLECULE_ID  INTEGER  PRIMARY KEY  AUTOINCREMENT  NOT NULL,
                             NAME         TEXT     UNIQUE       NOT NULL);""")

        # Creating MoleculeAtom table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeAtom
                             (MOLECULE_ID  INTEGER  NOT NULL,
                             ATOM_ID      INTEGER  NOT NULL,
                             PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                             FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                             FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID));""")

        # Creating MoleculeBond table
        self.conn.execute("""CREATE TABLE IF NOT EXISTS MoleculeBond
                             (MOLECULE_ID  INTEGER  NOT NULL,
                             BOND_ID      INTEGER  NOT NULL,
                             PRIMARY KEY (MOLECULE_ID, BOND_ID),
                             FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                             FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID));""")
    

    # Method to use indexing to set values inside a table
    def __setitem__(self, table, values):
        # Insert values to table named table
        self.conn.execute("""INSERT INTO {} VALUES (?, ?, ?, ?, ?, ?, ?);""".format(table), values)
        self.conn.commit()
    

    # Adding atom into the Atoms table in the database
    def add_atom(self, molname, atom):
        # Insert the atom into the database
        xVal = float(format(atom.atom.x, '.4f'))
        yVal = float(format(atom.atom.y, '.4f'))
        zVal = float(format(atom.atom.z, '.4f'))
        self.conn.execute("""INSERT 
                             INTO   Atoms  (ELEMENT_CODE, X, Y, Z) 
                             VALUES        (?, ?, ?, ?);""", (atom.atom.element, xVal, yVal, zVal))
        self.conn.commit()
        
        # Getting the atom id
        dataAtomID = self.conn.execute("""SELECT ATOM_ID FROM Atoms ORDER BY ATOM_ID DESC LIMIT 1;""")
        atomID = dataAtomID.fetchone()

        # Getting the molecule id
        dataMolID = self.conn.execute("""SELECT MOLECULE_ID FROM Molecules WHERE NAME=?""", (molname,))
        molID = dataMolID.fetchone()

        # Add entry into the MoleculeAtom table
        self.conn.execute("""INSERT INTO MoleculeAtom VALUES (?, ?);""", (int(molID[0]), int(atomID[0])))
        self.conn.commit()


    # Adding bond into the Bonds table in the database
    def add_bond(self, molname, bond):
        # Insert the bond into the database
        self.conn.execute("""INSERT 
                             INTO   Bonds (A1, A2, EPAIRS) 
                             VALUES       (?, ?, ?);""", (bond.bond.a1, bond.bond.a2, bond.bond.epairs))
        self.conn.commit()
        
        # Getting the bond id
        dataBondID = self.conn.execute("""SELECT BOND_ID FROM Bonds ORDER BY BOND_ID DESC LIMIT 1;""")
        bondID = dataBondID.fetchone()

        # Getting the molecule id
        dataMolID = self.conn.execute("""SELECT MOLECULE_ID FROM Molecules WHERE NAME=?""", (molname,))
        molID = dataMolID.fetchone()

        # Add entry into the MoleculeBond table
        self.conn.execute("""INSERT INTO MoleculeBond VALUES (?, ?);""", (int(molID[0]), int(bondID[0])))
        self.conn.commit()

    
    # Adding molecule into the Molecules table in the database
    def add_molecule(self, name, fp):
        mol = MolDisplay.Molecule() # Create a new molecule object
        mol.parse(fp) # Parsing a file

        # Insert the molecule into Molecules table
        self.conn.execute("""INSERT INTO Molecules (NAME) VALUES (?);""", (name,))
        self.conn.commit()

        # Add the atoms and bonds into the database
        for i in range(mol.atom_no):
            atom = mol.get_atom(i)
            atomWrapped = MolDisplay.Atom(atom)
            self.add_atom(name, atomWrapped)
        
        for i in range(mol.bond_no):
            bond = mol.get_bond(i)
            bondWrapped = MolDisplay.Bond(bond)
            self.add_bond(name, bondWrapped)


    # Loading molecule from the database
    def load_mol(self, name):
        # Create a mol object
        mol = MolDisplay.Molecule()

        # Getting all of the atoms in the database associated with a molecule name
        atomsDB = self.conn.execute("""SELECT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z FROM Atoms 
                                         INNER JOIN MoleculeAtom ON Atoms.ATOM_ID=MoleculeAtom.ATOM_ID 
                                         INNER JOIN Molecules ON MoleculeAtom.MOLECULE_ID=Molecules.MOLECULE_ID 
                                         WHERE Molecules.NAME = ? 
                                         ORDER BY Atoms.ATOM_ID ASC;""", (name,))
        
        atomsData = atomsDB.fetchall()

        # Append atoms into the mol object
        for atom in atomsData:
            mol.append_atom(atom[0], atom[1], atom[2], atom[3])
        
         # Getting all of the bonds in the database associated with a molecule name
        bondsDB = self.conn.execute("""SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS FROM Bonds 
                                         INNER JOIN MoleculeBond ON Bonds.BOND_ID=MoleculeBond.BOND_ID 
                                         INNER JOIN Molecules ON MoleculeBond.MOLECULE_ID=Molecules.MOLECULE_ID 
                                         WHERE Molecules.NAME = ? 
                                         ORDER BY Bonds.BOND_ID ASC;""", (name,))

        bondsData = bondsDB.fetchall()

        # Append bonds into the mol object
        for bond in bondsData:
            mol.append_bond(bond[0], bond[1], bond[2])

        return mol

    
    # Creating a radius dictionary
    def radius(self):
        radiusDict = {}

        # Fetching the ELEMENT_CODE and RADIUS data from the Elements table
        radiusDB = self.conn.execute("""SELECT ELEMENT_CODE, RADIUS FROM Elements;""")
        radiusData = radiusDB.fetchall()

        # Adding radius data to dictionary
        for data in radiusData:
            radiusDict[data[0]] = data[1]

        return radiusDict
    

    # Creating a dictionary containing element name and code as a key
    def element_name(self):
        elementNameDict = {}        
        
        # Fetching the ELEMENT_CODE and ELEMENT_NAME data from the Elements table
        elementNameDB = self.conn.execute("""SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements;""")
        elementNameData = elementNameDB.fetchall()

        # Adding element name data to dictionary
        for data in elementNameData:
            elementNameDict[data[0]] = data[1]
        
        return elementNameDict

    
    # Generate SVG for radial gradient
    def radial_gradients(self):
        radialGradientString = """"""

        # Fetching element name and the 3 colours from the Elements table
        elementDB = self.conn.execute("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements;""")
        elementData = elementDB.fetchall()

        # Writing radial gradient SVG for each elements
        for data in elementData:
            theID = html.escape(data[0])
            radialGradientString += (radialGradientSVG % (theID, data[1], data[2], data[3]))
        
        return radialGradientString
