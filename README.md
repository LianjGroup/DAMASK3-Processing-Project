# DAMASK3-Processing-Project
Author: Xuan Binh 

Stage 1: Convert your material.config file from DAMASK 2 to DAMASK 3

- Step 1: Adding your material.config file to folder convert_material_config_to_yaml
- Step 2: Open the file convert_material_config_to_yaml.ipynb and follow the instructions inside the file
- Step 3: If some error occurs during conversion, please check the file damask2_to_damask3_keywords.ipynb and add the missing mapping keys between damask 2 and damask 3. 

If you want to create a DAMASK 3 material.yaml file from scratch, please check the file generate_material_manual.ipynb instead

Stage 2: Convert your tensionX.load file from DAMASK 2 to DAMASK 3

- Step 1: Adding your tensionX.load file to folder convert_tensionX_load_to_yaml
- Step 2: Open the file convert_tensionX_load_to_yaml.ipynb and follow the instructions inside the file
- Step 3: If some error occurs during conversion, please check the file damask2_to_damask3_keywords.ipynb and add the missing mapping keys between damask 2 and damask 3 for tension_convert dictionary

If you want to create a DAMASK 3 load.yaml file from scratch, please check the file generate_tensionX_manual.ipynb instead

Stage 3: Generate the template files for DAMASK 3 
The template for DAMASK 3 simulation contains these files

- debug.yaml
- numerics.yaml
- material.geom file extracted from Dream3D
- euler_angles.txt extracted from end of material file from Dream3D
- preprocessing.sh
- postprocessing.sh

- Step 1: Create a folder with the name of your material under folder source/ (e.g. source/QP50)
- Step 2: Copy the material.yaml file generated from Stage 1 to the folder source/<material>
- Step 3: Copy the filte <material>.geom file extracted from Dream3D to the folder source/<material>


