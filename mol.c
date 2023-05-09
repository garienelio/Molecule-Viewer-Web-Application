#include "mol.h"

// Copy x, y, z, and element into atom
void atomset( atom *atom, char element[3], double *x, double *y, double *z ){
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

// Copy atom into x, y, z, and element
void atomget( atom *atom, char element[3], double *x, double *y, double *z ){
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

// Copy a1, a2, and epairs into bond
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;

    compute_coords(bond);
}

// Copy bond into a1, a2, and epairs
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ){
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

// malloc and setting a new molecule
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ){
    // Make a new area of memory
    molecule *newMolecule = malloc(sizeof(molecule));

    // If malloc has failed
    if(newMolecule == NULL){
        return NULL;
    }

    // Setting atoms
    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    newMolecule->atoms = malloc(atom_max * sizeof(struct atom));
    newMolecule->atom_ptrs = malloc(atom_max * sizeof(struct atom*));

    // If malloc has failed
    if(newMolecule->atoms == NULL || newMolecule->atom_ptrs == NULL){
        free(newMolecule);
        return NULL;
    }

    // Setting bonds
    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;
    newMolecule->bonds = malloc(bond_max * sizeof(struct bond));
    newMolecule->bond_ptrs = malloc(bond_max * sizeof(struct bond*));

    // If malloc has failed
    if(newMolecule->bonds == NULL || newMolecule->bond_ptrs == NULL){
        free(newMolecule);
        return NULL;
    }

    return newMolecule;
}

// Copying a molecule
molecule *molcopy( molecule *src ){
    // Create a new molecule
    molecule *newMolecule = molmalloc(src->atom_max, src->bond_max);

    // If malloc has failed
    if(newMolecule == NULL){
        return NULL;
    }

    // Append atoms into the new molecule
    for(int i = 0; i < src->atom_no; i++){
        atom a = src->atoms[i];
        molappend_atom(newMolecule, &a);
    }

    // Append bonds into the new molecule
    for(int i = 0; i < src->bond_no; i++){
        bond b = src->bonds[i];
        b.atoms = newMolecule->atoms;
        molappend_bond(newMolecule, &b);
    }

    return newMolecule;
}

// Freeing a molecule
void molfree( molecule *ptr ){
    // Freeing atoms arrays
    free(ptr->atom_ptrs);
    free(ptr->atoms);

    // Freeing bonds arrays
    free(ptr->bond_ptrs);
    free(ptr->bonds);

    // Free the molecule
    free(ptr);
}

// Adding an atom to molecule
void molappend_atom( molecule *molecule, atom *atom ){
    // If the array is full or max number is 0
    if(molecule->atom_max == 0){
        molecule->atom_max = 1;
        molecule->atoms = realloc(molecule->atoms, molecule->atom_max * sizeof(struct atom));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, molecule->atom_max * sizeof(struct atom*));

        // Exit if realloc fails
        if(molecule->atoms == NULL || molecule->atom_ptrs == NULL){
            fprintf(stderr, "molappend_atom has failed.\n");
            exit(-1);
        }
    }
    else if(molecule->atom_no == molecule->atom_max){
        molecule->atom_max = (molecule->atom_max) * 2;
        molecule->atoms = realloc(molecule->atoms, molecule->atom_max * sizeof(struct atom));
        molecule->atom_ptrs = realloc(molecule->atom_ptrs, molecule->atom_max * sizeof(struct atom*));

        // Exit if realloc fails
        if(molecule->atoms == NULL || molecule->atom_ptrs == NULL){
            fprintf(stderr, "molappend_atom has failed.\n");
            exit(-1);
        }

        // Make atom pointers to the new reallocated memory location
        for(int i = 0; i < molecule->atom_no; i++){
            molecule->atom_ptrs[i] = &molecule->atoms[i];
        }
    }

    // Insert to array
    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no += 1;
}

// Adding a bond to molecule
void molappend_bond( molecule *molecule, bond *bond ){
    // If the array is full or max number is 0
    if(molecule->bond_max == 0){
        molecule->bond_max = 1;
        molecule->bonds = realloc(molecule->bonds, molecule->bond_max * sizeof(struct bond));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, molecule->bond_max * sizeof(struct bond*));

        // Exit if realloc fails
        if(molecule->bonds == NULL || molecule->bond_ptrs == NULL){
            fprintf(stderr, "molappend_bond has failed.\n");
            exit(-1);
        } 
    }
    else if(molecule->bond_no == molecule->bond_max){
        molecule->bond_max = (molecule->bond_max) * 2;
        molecule->bonds = realloc(molecule->bonds, molecule->bond_max * sizeof(struct bond));
        molecule->bond_ptrs = realloc(molecule->bond_ptrs, molecule->bond_max * sizeof(struct bond*));

        // Exit if realloc fails
        if(molecule->bonds == NULL || molecule->bond_ptrs == NULL){
            fprintf(stderr, "molappend_bond has failed.\n");
            exit(-1);
        }

        // Make bond pointers to the new reallocated memory location
        for(int i = 0; i < molecule->bond_no; i++){
            molecule->bond_ptrs[i] = &molecule->bonds[i];
        }
    }

    // Insert to array
    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no += 1;
}

// qsort helper for atom
int compareAtom( const void *a, const void *b ){
    struct atom **atom1, **atom2;
    double val1, val2;

    atom1 = (struct atom **)a;
    atom2 = (struct atom **)b;

    val1 = (*atom1)->z;
    val2 = (*atom2)->z;

    double result = val1 - val2;

    if(result < 0){
        return -1;
    } else if(result > 0){
        return 1;
    }
    return 0;
}

// qsort helper for bond
int compareBond( const void *a, const void *b ){
    struct bond **bond1, **bond2;
    double val1, val2;

    bond1 = (struct bond **)a;
    bond2 = (struct bond **)b;

    val1 = (*bond1)->z;
    val2 = (*bond2)->z;
    
    double result = val1 - val2;

    if(result < 0){
        return -1;
    } else if(result > 0){
        return 1;
    }
    return 0;
}

// Sorting the molecule
void molsort( molecule *molecule ){
    // Sorting the atoms
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(struct atom*), compareAtom);

    // Sorting the bonds
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(struct bond*), compareBond);
}

// Rotation on x axis
void xrotation( xform_matrix xform_matrix, unsigned short deg ){
    // Change degree to radian
    double degInRad = deg * (M_PI / 180);

    // Set the matrix
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(degInRad);
    xform_matrix[1][2] = -sin(degInRad);
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(degInRad);
    xform_matrix[2][2] = cos(degInRad);
}

// Rotation on y axis
void yrotation( xform_matrix xform_matrix, unsigned short deg ){
    // Change degree to radian
    double degInRad = deg * (M_PI / 180);

    // Set the matrix
    xform_matrix[0][0] = cos(degInRad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(degInRad);
    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = -sin(degInRad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(degInRad);
}

// Rotation on z axis
void zrotation( xform_matrix xform_matrix, unsigned short deg ){
    // Change degree to radian
    double degInRad = deg * (M_PI / 180);

    // Set the matrix
    xform_matrix[0][0] = cos(degInRad);
    xform_matrix[0][1] = -sin(degInRad);
    xform_matrix[0][2] = 0;
    xform_matrix[1][0] = sin(degInRad);
    xform_matrix[1][1] = cos(degInRad);
    xform_matrix[1][2] = 0;
    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

// Do matrix multiplication on x, y, and z for rotations
void mol_xform( molecule *molecule, xform_matrix matrix ){
    for(int i = 0; i < molecule->atom_no; i++){
        double xVal, yVal, zVal;

        xVal = molecule->atoms[i].x;
        yVal = molecule->atoms[i].y;
        zVal = molecule->atoms[i].z;

        molecule->atoms[i].x = (matrix[0][0] * xVal) + (matrix[0][1] * yVal) + (matrix[0][2] * zVal);
        molecule->atoms[i].y = (matrix[1][0] * xVal) + (matrix[1][1] * yVal) + (matrix[1][2] * zVal);
        molecule->atoms[i].z = (matrix[2][0] * xVal) + (matrix[2][1] * yVal) + (matrix[2][2] * zVal);
    }

    for(int i = 0; i < molecule->bond_no; i++){
        compute_coords(&(molecule->bonds[i]));
    }
}

void compute_coords( bond *bond ){
    // Copying the x and y values for both atoms
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    // Calculating the bond z value
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

    // Calculating the bond length
    double xDif = bond->x2 - bond->x1;
    double yDif = bond->y2 - bond->y1;
    bond->len = sqrt((xDif * xDif) + (yDif * yDif));

    // Calculate dx and dy
    bond->dx = xDif / bond->len;
    bond->dy = yDif / bond->len;
}
