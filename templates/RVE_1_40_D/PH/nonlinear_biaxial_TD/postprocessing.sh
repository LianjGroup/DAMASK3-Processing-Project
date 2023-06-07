#!/bin/bash
# created: Oct 19, 2022 22:22 PM
# author: xuanbinh
#SBATCH --account=project_2004956
#SBATCH --partition=test
#SBATCH --time=00:15:00
#SBACTH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH -J CPparameter_test
#SBATCH -e CPparameter_test
#SBATCH --mail-type=ALL
#SBATCH --mail-user=binh.nguyen@aalto.fi

### Since postprocessing does not used DAMASK_spectral, this script cannot make use of MPI. 

module load python-data

### Change to your current working directory
cd $PWD

### Set unlimited stack size and locked memory
ulimit -s unlimited 
ulimit -l unlimited

### Enabling environments
export PATH=$PATH:=/projappl/project_2004956/damask-3.0.0-alpha7:/projappl/project_2004956/damask-3.0.0-alpha7/processing
export HDF5_USE_FILE_LOCKING=FALSE

### Creating DAMASK postprocessing folder
mkdir -p $PWD/postProc

### Postprocessing results from the hdf5 output file
python /projappl/project_2004956/damask-3.0.0-alpha7/processing/postprocessing.py $PWD/RVE_1_40_D_tensionX.hdf5 $PWD/postProc