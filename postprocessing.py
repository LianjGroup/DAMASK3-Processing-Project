# 
# DAMASK is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import numpy as np
import damask
import yaml
from yaml.loader import BaseLoader
from subprocess import call
import pandas as pd
import shutil

# Check if the correct number of arguments are provided
if len(sys.argv) != 3:
    print("Usage error: plase use this script with 2 arguments\npython postprocessing.py <simulationPath> <outputFile>")
    sys.exit(1)

# Get the arguments
currentPath = sys.argv[1]
materialOutputExtension = sys.argv[2]

splitMaterialOutputExtension = materialOutputExtension.split(".")
material = splitMaterialOutputExtension[0]
outputExtension = splitMaterialOutputExtension[1]

outputPath = f"{currentPath}/{materialOutputExtension}"

outputPathCopy = f"{currentPath}/{material}_copy.{outputExtension}"

# Copy the source hdf5 file to the destination directory with a new name
command = f"cp {outputPath} {outputPathCopy}"

# Execute the command
return_code = call(command, shell=True)

# Print the paths for demonstration
#print("HDF5 Output Path:", outputPath)
#print("Postprocessing Path:", postprocessingPath)

def getMean1DAcrossPhases(result, attribute):
    # Increment -> Phase -> np.array of shape (num_grains_of_phase,)
    # Return np.array of shape (num_increments,)
    allIncrements = result.get(attribute).keys()

    allIncrements = list(allIncrements)
    allPhases = result.get(attribute)[allIncrements[0]].keys()
    allPhases = list(allPhases)
    #print(allIncrements)
    #print(allPhases)
    mean_attribute = []
    attribute_dict = result.get(attribute)

    # for increment in allIncrements:
    #     increment_values = []
    #     for phase in allPhases:
    #         increment_values.append(np.mean(attribute_dict[increment][phase]).item())
    #     mean_attribute.append(np.mean(increment_values).item())
    # return mean_attribute

    for increment in allIncrements:
        increment_values = []
        for phase in allPhases:
            increment_values.extend(attribute_dict[increment][phase])
        mean_attribute.append(np.mean(increment_values).item())
    return mean_attribute

def getMeanTensorAcrossPhases(result, attribute):
    # Increment -> Phase -> np.array of shape (num_grains_of_phase, 3, 3)
    # Return np.array of shape (num_increments, 3, 3)
    
    allIncrements = result.get(attribute).keys()
    
    allIncrements = list(allIncrements)
    allPhases = result.get(attribute)[allIncrements[0]].keys()
    allPhases = list(allPhases)
    #print(allIncrements)
    #print(allPhases)
    
    attribute_dict = result.get(attribute)

    mean_attribute = np.empty((0,3,3))
    # Use np.concatenate
    for increment in allIncrements:
        increment_values = np.empty((0,3,3))
        for phase in allPhases:
            increment_values = np.concatenate((increment_values, attribute_dict[increment][phase]), axis=0)
        mean_attribute = np.concatenate((mean_attribute, np.mean(increment_values,axis=0)[np.newaxis,:,:]), axis=0)
        #mean_attribute.append(np.mean(increment_values,axis=0))
    return mean_attribute

def getSum1DAcrossPhases(result, attribute):
    # Increment -> Phase -> np.array of shape (num_grains_of_phase,)
    # Return np.array of shape (num_increments,)
    allIncrements = result.get(attribute).keys()

    allIncrements = list(allIncrements)
    allPhases = result.get(attribute)[allIncrements[0]].keys()
    allPhases = list(allPhases)
    sum_attribute = []
    attribute_dict = result.get(attribute)

    for increment in allIncrements:
        increment_values = []
        for phase in allPhases:
            increment_values.extend(attribute_dict[increment][phase])
        sum_attribute.append(np.sum(increment_values).item())
    return sum_attribute

with open(f'{currentPath}/material.yaml', 'r') as stream:
    material_yaml = yaml.load(stream, Loader=BaseLoader)

phases = list(material_yaml['phase'].keys())

# if plastic output exists:
all_outputs = material_yaml['phase'][phases[0]]['mechanical']['output']
if 'output' in material_yaml['phase'][phases[0]]['mechanical']['plastic']:
    plastic_outputs = material_yaml['phase'][phases[0]]['mechanical']['plastic']['output']
    outputs = all_outputs + plastic_outputs
else:
    outputs = all_outputs

CPLaw = material_yaml['phase'][phases[0]]['mechanical']['plastic']['type']

if CPLaw == 'phenopowerlaw':
    CPLaw = 'PH'
elif CPLaw == 'dislotwin':
    CPLaw = 'DB'

numPhases = len(phases)

# Create an empty DataFrame
df = pd.DataFrame()

result = damask.Result(outputPathCopy)

#print("Reading file successful")
# https://damask.mpie.de/documentation/examples/add_field_data.html
# add deformation gradient rate F and Piola–Kirchhoff stress P

# Adding the increments and times to the DataFrame
increments = result.increments_in_range(start=0,end=10e9)
df["inc"] = increments

times = result.times_in_range(start=0,end=10e9)
df["time"] = times

# Now we add data from the output fields
# Assume we must have at least P and F output
result.add_stress_Cauchy('P','F')

result.add_strain('F','U')
result.add_strain('F','V')

# Add the Mises equivalent of the Cauchy stress 'sigma'
result.add_equivalent_Mises('sigma')

# Add the Mises equivalent of the spatial logarithmic strain 'epsilon_V^0.0(F)'
result.add_equivalent_Mises('epsilon_V^0.0(F)')

if 'F_p' in outputs:
    result.add_strain('F_p','U')
    result.add_strain("F_p",'V')
    result.add_equivalent_Mises('epsilon_U^0.0(F_p)')

#################################
#################################
#################################

# The parts below is for 1 phase and many phases postprocessing
if numPhases == 1:

    # True stress - true strain curve
    trueStress = [np.average(s) for s in result.get('sigma_vM').values()]
    trueStrain = [np.average(e) for e in result.get('epsilon_V^0.0(F)_vM').values()]

    # Adding equivalent von Mises stress and logarithmic strain to the DataFrame
    df["Mises(Cauchy)"] = trueStress
    df["Mises(ln(V))"] = trueStrain

    # Add the stress and strain tensor
    F = np.array(list(result.get('F').values()))
    F = np.mean(F, axis=1)

    # Adding the stress and strain tensor to the DataFrame
    epsilonV00F = np.array(list(result.get('epsilon_V^0.0(F)').values()))
    epsilonV00F = np.mean(epsilonV00F, axis=1)

    for i in range(3):
        for j in range(3):
            index = i * 3 + j + 1
            df[f'{index}_f'] = F[:,i,j]
        
    for i in range(3):
        for j in range(3):
            index = i * 3 + j + 1
            df[f'{index}_ln(V)'] = epsilonV00F[:,i,j]

    if 'F_p' in outputs:
        # Lankford coefficient - Plastic strain ratio curve 
        epsilon_avg = np.array([np.average(eps,0) for eps in result.get('epsilon_U^0.0(F_p)').values()])
        Rvalue_coeff = epsilon_avg[:,1,1]/epsilon_avg[:,2,2]
        Rvalue_strain = np.array([np.average(strain) for strain in result.get('epsilon_U^0.0(F_p)_vM').values()])
        df['r-value-coeff'] = Rvalue_coeff
        df['r-value-strain'] = Rvalue_strain

    # Add the total mobile and dipole dislocation density
    if 'rho_mob' in outputs:
        if CPLaw == 'DB':
            result.add_calculation('np.sum(#rho_mob#,axis=1)','rho_mob_total','1/m2','total mobile dislocation density')
            rho_mob_total = np.array([np.average(s) for s in result.get('rho_mob_total').values()])
            df['rho_mob_total'] = rho_mob_total
    if 'rho_dip' in outputs:
        if CPLaw == 'DB':
            result.add_calculation('np.sum(#rho_dip#,axis=1)','rho_dip_total','1/m2','total dislocation dipole density')
            rho_dip_total = np.array([np.average(s) for s in result.get('rho_dip_total').values()])
            df['rho_dip_total'] = rho_dip_total
    if 'rho_mob' in outputs and 'rho_dip' in outputs:
        if CPLaw == 'DB':
            result.add_calculation('np.sum(#rho_mob#+#rho_dip#,axis=1)','rho_total','1/m2','total dislocation density') 
            rho_total = rho_mob_total + rho_dip_total
            df['rho_total'] = rho_total 


# Multiple phases:
else:
    trueStress = getMean1DAcrossPhases(result, 'sigma_vM') 
    trueStrain = getMean1DAcrossPhases(result, 'epsilon_V^0.0(F)_vM')

    # Adding equivalent von Mises stress and logarithmic strain to the DataFrame
    df["Mises(Cauchy)"] = trueStress
    df["Mises(ln(V))"] = trueStrain

    # Add the stress and strain tensor
    F = getMeanTensorAcrossPhases(result, 'F')
    epsilonV00F = getMeanTensorAcrossPhases(result, 'epsilon_V^0.0(F)')

    for i in range(3):
        for j in range(3):
            index = i * 3 + j + 1
            df[f'{index}_f'] = F[:,i,j]
        
    for i in range(3):
        for j in range(3):
            index = i * 3 + j + 1
            df[f'{index}_ln(V)'] = epsilonV00F[:,i,j]

    epsilon_avg = getMeanTensorAcrossPhases(result, 'epsilon_U^0.0(F_p)')
    Rvalue_coeff = epsilon_avg[:,1,1]/epsilon_avg[:,2,2]
    Rvalue_strain = getMean1DAcrossPhases(result, 'epsilon_U^0.0(F_p)_vM')
    df['r-value-coeff'] = Rvalue_coeff
    df['r-value-strain'] = Rvalue_strain

    # Add the total mobile and dipole dislocation density
    if 'rho_mob' in outputs:
        if CPLaw == 'DB':
            rho_mob_total = getSum1DAcrossPhases(result, 'rho_mob')
            rho_mob_total = np.array(rho_mob_total)
            df['rho_mob_total'] = rho_mob_total
    if 'rho_dip' in outputs:
        if CPLaw == 'DB':
            rho_dip_total = getSum1DAcrossPhases(result, 'rho_dip')
            rho_dip_total = np.array(rho_dip_total)
            df['rho_dip_total'] = rho_dip_total
    if 'rho_mob' in outputs and 'rho_dip' in outputs:
        if CPLaw == 'DB':
            rho_total = rho_mob_total + rho_dip_total
            df['rho_total'] = rho_total 

# Postprocessing path
postprocessingPath = f"{currentPath}/postProc"

# Save DataFrame as xlsx file
df.to_excel(f'{postprocessingPath}/{material}_tensionX.xlsx', index=False)

# Save DataFrame as txt file
df.to_csv(f'{postprocessingPath}/{material}_tensionX.txt', index=False, sep ='\t')

# Remove the copied hdf5 output file
os.remove(outputPathCopy)

# np.save(f"{postprocessingPath}/trueStress.npy", trueStress)
# np.save(f"{postprocessingPath}/trueStrain.npy", trueStrain)
# np.save(f"{postprocessingPath}/Rvalue_coeff.npy", Rvalue_coeff)
# np.save(f"{postprocessingPath}/Rvalue_strain.npy", Rvalue_strain)
# np.save(f"{postprocessingPath}/rho_mob_total.npy", rho_mob_total)
# np.save(f"{postprocessingPath}/rho_dip_total.npy", rho_dip_total)
# np.save(f"{postprocessingPath}/rho_total.npy", rho_total)

# increment_0 (0.0 s)
#   phase
#     Aluminum
#       mechanical
#         F / 1: deformation gradient
#         F_e / 1: elastic deformation gradient
#         F_p / 1: plastic deformation gradient
#         L_p / 1/s: plastic velocity gradient
#         O / q_0 (q_1 q_2 q_3): crystal orientation as quaternion
#         P / Pa: first Piola-Kirchhoff stress
#         epsilon_V^0.0(F) / 1: strain tensor of F (deformation gradient)
#         epsilon_V^0.0(F)_vM / 1: Mises equivalent strain of epsilon_V^0.0(F) (strain tensor of F (deformation gradient))
#         epsilon_V^0.0(F_p) / 1: strain tensor of F_p (plastic deformation gradient)
#         rho_dip / 1/m²: dislocation dipole density
#         rho_dip_total / 1/m²: total dislocation dipole density (formula: np.sum(#rho_dip#,axis=1))
#         rho_mob / 1/m²: mobile dislocation density
#         rho_mob_total / 1/m²: total mobile dislocation density (formula: np.sum(#rho_mob#,axis=1))
#         sigma / Pa: Cauchy stress calculated from P (first Piola-Kirchhoff stress) and F (deformation gradient)
#         sigma_vM / Pa: Mises equivalent stress of sigma (Cauchy stress calculated from P (first Piola-Kirchhoff stress) and F (deformation gradient))
#   homogenization
#     SX
