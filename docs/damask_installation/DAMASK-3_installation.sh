#!/bin/bash

# Esko Järvinen, CSC - IT Center for Science Ltd, 24 Nov 2022

instRoot=/scratch/project_2004956/damask3

echo; 
echo "  This script will install use environment for DAMASK-3""." ; echo
echo "  The installation will be done into the current directory :"
echo " " `echo $PWD` ; echo

read -r -p "Is the directory OK? [y/N] " response
if ! [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]
then
    echo; echo "  OK - change the directory."; echo
    exit
else
    echo;
fi

echo; 
echo "  DAMASK-3 requires installation of Petsc made by the user." ; echo

read -r -p "  Please, give the installation path to the Petsc: " petscPath
if ! [[ -f $petscPath/include/petsc.h ]]
then
    echo; echo "  *** Looks like Petsc installation is not correct."
    echo "  *** Look more information in the file DAMASK-3_PETSC_INSTALLATION_Puhti.txt"; echo
    cp $instRoot/petsc_installation.txt .
    exit
else
    echo;
fi

( set -x ; mkdir inst-3.0 )
( set -x ; cp $instRoot/ENV_FOR_DAMASK3_Puhti.txt .)
( set -x ; cp $instRoot/DAMASK-3_DOWNLOAD_AND_COMPILATION_Puhti.txt .)
( set -x ; sed -i -e "s|XXYYZZ|$PWD|g" ENV_FOR_DAMASK3_Puhti.txt )
( set -x ; sed -i -e "s|XXYYZZ|$PWD|g" DAMASK-3_DOWNLOAD_AND_COMPILATION_Puhti.txt )
( set -x ; sed -i -e "s|USERPETSCDIR|$petscPath|g" ENV_FOR_DAMASK3_Puhti.txt )


echo; echo "  Next, continue with compilation.  See instructions given in the file "
echo " download_install_damask.txt"; echo
