#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import damask


# In[ ]:


fname = 'RVE_1_40_D'
grid = damask.Grid.load_ASCII(f'{fname}.geom')
grid.save(fname)


# In[ ]:


damask.Config("""
grid:
  itmin: 4
  itmax: 40
  maxCutBack: 50
""").save('numerics.yaml',default_flow_style = False)


# In[ ]:


damask.Config("""
solver:
  mechanical: spectral_basic

loadstep:
  - discretization:
      t: 50
      N: 50
    f_out: 2
    boundary_conditions:
      mechanical:
        dot_F: [[x, 0, 0],
                [0, 1.0e-4, 0],
                [0, 0, x]]
        P: [[0, x, x],
            [x, x, x],
            [x, x, 0]]
  - discretization:
      t: 2000
      N: 1000
    f_out: 50
    boundary_conditions:
      mechanical:
        dot_F: [[x, 0, 0],
                [0, 1.0e-4, 0],
                [0, 0, x]]
        P: [[0, x, x],
            [x, x, x],
            [x, x, 0]]
   
""").save('tensionX.yaml')


# In[ ]:


mat = damask.ConfigMaterial("""
homogenization:

  SX:
    N_constituents: 1
    mechanical:
      type: pass

phase:

  Al:
    lattice: cF
    mechanical:
      output: [F, P, O]
      elastic:
        type: Hooke
        C_11:                     107e9
        C_12:                     52e9
        C_44:                     26e9
      plastic:
        type: phenopowerlaw
        Nslip:                   12
        gdot0_slip:              0.001
        n_slip:                  20
        tau0_slip:                 70e6
        tausat_slip:               120e6
        a_slip:                  1.2 
        h0_slipslip:             1e9
        interaction_slipslip:    1 1 1 1 1 1
        atol_resistance:         1e5
""").material_add(O=damask.Rotation.from_random(shape=grid.N_materials),
                  phase='Al',
                  homogenization='SX')
mat.save()


# In[ ]:




