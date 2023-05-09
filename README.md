# Molecule Viewer Web Application

## Project Description 📝

This molecule viewer web application allows you to view the molecular structures of molecules from uploaded SDF files. <br>
This web application has the following functionalities:
- Adding and removing elements.
- Upload your own molecule SDF files.
- Display the molecules.
- Rotate the molecules on x, y, and z axis to view the molecule from different angles.

## Usage 💻
NOTE: This web application was made to be used in University of Guelph's server. <br> makefile might need to be modified to run the application on your system. <br><br>
Enter the following in your terminal to run the program:
```bash
make

export LD_LIBRARY_PATH=.

python3 server.py 59430
```
Go to your web browser and enter http://localhost:59430/index.html

## Languages and Tools Used 🛠️

![C](https://img.shields.io/badge/C-00599C?style=for-the-badge&logo=c&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![jQuery](https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white)
![VSCode](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![Codepen](https://img.shields.io/badge/Codepen-000000?style=for-the-badge&logo=codepen&logoColor=white)
![GitLab](https://img.shields.io/badge/GitLab-330F63?style=for-the-badge&logo=gitlab&logoColor=white)

## Project Development 🧑🏻‍💻

- Developed a C library to represent and manipulate the molecules.
- Wrote a python script to generate the SVG image of the molecule and implements the C library by using SWIG.
- Created a SQLite database to store data from the uploaded molecule SDF files.
- Built the front end using HTML/CSS and jQuery, as well as the server using Python HTTP.
