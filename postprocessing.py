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
import pandas as pd

# Check if the correct number of arguments are provided
if len(sys.argv) != 4:
    print("Usage error: plase use this script with 3 arguments\npython postprocessing.py <hdf5OutputPath> <postprocessingPath> <material>")
    sys.exit(1)

# Get the arguments
hdf5OutputPath = sys.argv[1]
postprocessingPath = sys.argv[2]
material = sys.argv[3]

# Check if the HDF5 file exists
if not os.path.isfile(hdf5OutputPath):
    print(f"Error: HDF5 file '{hdf5OutputPath}' does not exist.")
    sys.exit(1)

# Print the paths for demonstration
#print("HDF5 Output Path:", hdf5OutputPath)
#print("Postprocessing Path:", postprocessingPath)

result = damask.Result(hdf5OutputPath)
#print("Reading file successful")
# https://damask.mpie.de/documentation/examples/add_field_data.html
# add deformation gradient rate F and Piola–Kirchhoff stress P

result.add_stress_Cauchy('P','F')
result.add_strain('F','U')
result.add_strain('F','V')
result.add_strain('F_p','U')
result.add_strain("F_p",'V')

# Add the Mises equivalent of the Cauchy stress 'sigma'
# Add the Mises equivalent of the spatial logarithmic strain 'epsilon_V^0.0(F)'
result.add_equivalent_Mises('sigma')
result.add_equivalent_Mises('epsilon_V^0.0(F)')
result.add_equivalent_Mises('epsilon_U^0.0(F_p)')

# Add the total mobile and dipole dislocation density
result.add_calculation('np.sum(#rho_mob#,axis=1)','rho_mob_total','1/m2','total mobile dislocation density')
result.add_calculation('np.sum(#rho_dip#,axis=1)','rho_dip_total','1/m2','total dislocation dipole density')

increments = result.increments_in_range(start=0,end=10e9)

times = result.times_in_range(start=0,end=10e9)

F = np.array(list(result.get('F').values()))
F = np.mean(F, axis=1)

epsilonV00F = np.array(list(result.get('epsilon_V^0.0(F)').values()))
epsilonV00F = np.mean(epsilonV00F, axis=1)

# True stress - true strain curve
trueStress = [np.average(s) for s in result.get('sigma_vM').values()]
trueStrain = [np.average(e) for e in result.get('epsilon_V^0.0(F)_vM').values()]

# Lankford coefficient - Plastic strain ratio curve 
epsilon_avg = np.array([np.average(eps,0) for eps in result.get('epsilon_U^0.0(F_p)').values()])
Rvalue_coeff = epsilon_avg[:,1,1]/epsilon_avg[:,2,2]
Rvalue_strain = np.array([np.average(strain) for strain in result.get('epsilon_U^0.0(F_p)_vM').values()])

# Dislocation density
mobile = result.get('rho_mob_total')
dipole = result.get('rho_dip_total')

rho_mob_total = np.array([np.average(s) for s in result.get('rho_mob_total').values()])
rho_dip_total = np.array([np.average(s) for s in result.get('rho_dip_total').values()])
rho_total = rho_mob_total + rho_dip_total

# Create an empty DataFrame
df = pd.DataFrame()

df["inc"] = increments
df["time"] = times
df['r-value-coeff'] = Rvalue_coeff
df['r-value-strain'] = Rvalue_strain
df['rho_mob_total'] = rho_mob_total
df['rho_dip_total'] = rho_dip_total
df['rho_total'] = rho_total 

for i in range(3):
    for j in range(3):
        index = i * 3 + j + 1
        df[f'{index}_f'] = F[:,i,j]
    
for i in range(3):
    for j in range(3):
        index = i * 3 + j + 1
        df[f'{index}_ln(V)'] = epsilonV00F[:,i,j]

df["Mises(Cauchy)"] = trueStress
df["Mises(ln(V))"] = trueStrain

# Save DataFrame as xlsx file
df.to_excel(f'{postprocessingPath}/{material}_tensionX.xlsx', index=False)

# Save DataFrame as txt file
df.to_csv(f'{postprocessingPath}/{material}_tensionX.txt', index=False, sep ='\t')

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
