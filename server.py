from http.server import HTTPServer, BaseHTTPRequestHandler
import sys     # to get command line argument for port
import urllib  # code to parse for data
import html
import molsql
import MolDisplay
import io
import molecule


# Connect to database and Create MolDisplay object
dbObj = molsql.Database(reset=False)
dbObj.create_tables()

# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = ['/index.html', '/editElements.html', '/moleculesList.html', '/uploadSDF.html', '/style.css', '/editElementsScript.js', '/uploadSDFScript.js', '/moleculesListScript.js']

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # used to GET a file from the list ov public_files, above
        if self.path in public_files:   # make sure it's a valid file
            self.send_response(200);  # OK
            self.send_header("Content-type", "text/html")

            fp = open(self.path[1:])
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read()
            fp.close()

            if self.path == '/editElements.html':
                replaceCode = """"""
                elementData = dbObj.conn.execute("""SELECT * FROM Elements;""")
                eData = elementData.fetchall()

                if len(eData) != 0:
                    for data in eData:
                        eCodeFormatted = html.escape(data[1])
                        eNameFormatted = html.escape(data[2])
                        replaceCode += """<option value="{}">{}: {}</option>""".format(eCodeFormatted, eCodeFormatted, eNameFormatted)
                    replaceCode += """</select>\n"""
                    page = page.replace('</select>', replaceCode)

            # Handling for moleculeList.html
            if self.path == '/moleculesList.html':
                replaceCode = """<select id="moleculeList">"""
                moleculeData = dbObj.conn.execute("""SELECT * FROM Molecules;""")
                mData = moleculeData.fetchall()

                if len(mData) != 0:
                    # Adding options into the html page
                    for data in mData:
                        mNameFormatted = html.escape(data[1])
                        mNum = data[0]

                        # Get atom count
                        atomData = dbObj.conn.execute("""SELECT * FROM MoleculeAtom WHERE MOLECULE_ID=?""", (mNum,))
                        atomCount = atomData.fetchall()

                        # Get bond count
                        bondData = dbObj.conn.execute("""SELECT * FROM MoleculeBond WHERE MOLECULE_ID=?""", (mNum,))
                        bondCount = bondData.fetchall()

                        replaceCode += """<option value="{}">{} ({} Atoms, {} Bonds)</option>""".format(mNameFormatted, mNameFormatted, len(atomCount), len(bondCount))
                    replaceCode += "</select>\n"
                    page = page.replace('<select id="moleculeList"></select>', replaceCode)

            # create and send headers
            self.send_header("Content-length", len(page))
            self.end_headers()

            # send the contents
            self.wfile.write(bytes(page, "utf-8"))

        else:
            # if the requested URL is not one of the public_files
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))



    def do_POST(self):
        if self.path == "/add.html":
            # Handling the adding element in editElements Page

            # Reading the data recieved from the form and convert it
            contentLength = int(self.headers['Content-Length'])
            formDataByte = self.rfile.read(contentLength)
            dataAsDictionary = urllib.parse.parse_qs(formDataByte.decode('utf-8'))

            # Getting the Data
            elementNumber = int(dataAsDictionary['eNumber'][0])
            elementCode = dataAsDictionary['eCode'][0]
            elementName = dataAsDictionary['eName'][0]
            elementColor1 = dataAsDictionary['eColor1'][0][1:]
            elementColor2 = dataAsDictionary['eColor2'][0][1:]
            elementColor3 = dataAsDictionary['eColor3'][0][1:]
            elementRadius = dataAsDictionary['eRadius'][0]

            # Check if the Element Code is already in it
            eCodeData = dbObj.conn.execute("""SELECT ELEMENT_CODE FROM Elements WHERE ELEMENT_CODE = ?""", (elementCode,))
            elCode = eCodeData.fetchone()

            # Data insertion into database
            if elCode is None:
                dbObj['Elements'] = (elementNumber, elementCode, elementName, elementColor1, elementColor2, elementColor3, elementRadius)

                # Send success message if success
                message = "Element successfully added to the database"
            else:
                # Send failed message if failed
                message = "Element already exist. Try Again."

            self.send_response(200); # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))

        
        elif self.path == "/remove.html":
            # Handling the remove element in editElements Page

            # Reading the data received from the form and convert it
            contentLength = int(self.headers['Content-Length'])
            formDataByte = self.rfile.read(contentLength)
            dataAsDictionary = urllib.parse.parse_qs(formDataByte.decode('utf-8'))

            # Getting the data
            theElementCode = dataAsDictionary['element'][0]

            # Data deletion from the sql database
            dbObj.conn.execute("""DELETE FROM Elements WHERE ELEMENT_CODE = ?""", (theElementCode,))
            dbObj.conn.commit()

            message = "The element has been deleted"
            self.send_response(200); # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))


        elif self.path == "/uploadSDFFile.html":
            # Reading the data received from the form and convert it
            contentLength = int(self.headers['Content-Length'])
            content = self.rfile.read(contentLength)
            contentMod = io.BytesIO(content)
            contentMod = io.TextIOWrapper(contentMod)
            contentModCheck = contentMod

            # Get the Molecule Name
            for i in range(3):
                contentMod.readline()
            moleculeName = contentMod.readline()

            molNames = dbObj.conn.execute("""SELECT NAME FROM Molecules WHERE NAME=?""", (moleculeName,))
            molNamesList = molNames.fetchone()

            if molNamesList is not None:
                message = "Molecule name is already used.\n Please enter a new name."
            else:
                # Get the Molecule file
                for i in range(4):
                    contentMod.readline()
                    
                try:
                    dbObj.add_molecule(moleculeName, contentMod)
                    message = "Molecule uploaded"
                except:
                    message = "Could not read the SDF File."

            self.send_response(200); # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))


        elif self.path == "/displayMolecule.html":
            # Reading the data recieved from the form and convert it
            contentLength = int(self.headers['Content-Length'])
            formDataByte = self.rfile.read(contentLength)
            dataAsDictionary = urllib.parse.parse_qs(formDataByte.decode('utf-8'))

            # Getting the data
            theMolecule = dataAsDictionary['molSelected'][0]

            # Getting the molecule display
            MolDisplay.radius = dbObj.radius()
            MolDisplay.element_name = dbObj.element_name()
            MolDisplay.header += dbObj.radial_gradients()

            # Generating the molecule SVG
            mol = dbObj.load_mol(theMolecule)
            mol.sort()
            moleculeSVG = mol.svg()

            # Send response
            self.send_response(200); # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(moleculeSVG))
            self.end_headers()
            self.wfile.write(bytes(moleculeSVG, "utf-8"))


        elif self.path == "/rotateMolecule.html":
            # Reading the data recieved from the form and convert it
            contentLength = int(self.headers['Content-Length'])
            formDataByte = self.rfile.read(contentLength)
            dataAsDictionary = urllib.parse.parse_qs(formDataByte.decode('utf-8'))

            # Getting the data
            theMol = dataAsDictionary['theMolecule'][0]
            axis = dataAsDictionary['theAxis'][0]
            degree = dataAsDictionary['theDegree'][0]
            theDegree = int(degree)

            MolDisplay.radius = dbObj.radius()
            MolDisplay.element_name = dbObj.element_name()
            MolDisplay.header += dbObj.radial_gradients()

            # Generating the molecule SVG
            mol = dbObj.load_mol(theMol)
            
            if axis == 'x':
                mRot = molecule.mx_wrapper(theDegree, 0, 0)
                mol.xform(mRot.xform_matrix)
            elif axis == 'y':
                mRot = molecule.mx_wrapper(0, theDegree, 0)
                mol.xform(mRot.xform_matrix)
            elif axis == 'z':
                mRot = molecule.mx_wrapper(0, 0, theDegree)
                mol.xform(mRot.xform_matrix)

            mol.sort()
            rotatedSVG = mol.svg()

            # Send response
            self.send_response(200); # OK
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(rotatedSVG))
            self.end_headers()
            self.wfile.write(bytes(rotatedSVG, "utf-8"))

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))




httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()
