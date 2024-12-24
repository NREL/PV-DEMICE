#!/usr/bin/env python
# coding: utf-8

# # SIPS: QUIP SERIES
# This journal explores the case studies of the SIPS 2025 project understanding the implications of repowering and module reuse. This compliments analyses conducted in SAM and PV Watts. Below are the Residential, Commercial, and Utility scale case studies

# In[ ]:


#setup
import numpy as np
import pandas as pd
import os,sys
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.express as px

import PV_ICE

cwd = os.getcwd() #grabs current working directory

testfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'TEMP' / 'MESC-NRELStdScens')
inputfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines'/'NRELStdScenarios')
baselinesfolder = str(Path().resolve().parent.parent /'PV_ICE' / 'baselines')
supportMatfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines' / 'SupportingMaterial')
#altBaselinesfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines' / 'Energy_CellModuleTechCompare')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("pyplot ", plt.matplotlib.__version__)
print("PV_ICE version ", PV_ICE.__version__)


# In[ ]:


sim1 = PV_ICE.Simulation(name='SIPS', path=testfolder)


# ## Residential Case Study
# This case study considers a residential system where the PV system is not at technical end of life (installed 2015), but the roof needs replacing in 2024. The owner has the option of keeping the old system or replacing the PV system.

# In[ ]:


#c-Si
MATERIALS = ['glass','aluminium_frames','silver','silicon', 'copper', 'encapsulant', 'backsheet']
moduleFile = os.path.join(baselinesfolder, 'baseline_modules_mass_US_updatedT50T90.csv')
#CdTe
#MATERIALS_CdTe = ['glass_cdte','aluminium_frames_cdte', 'copper_cdte', 'encapsulant_cdte','cadmium','tellurium']
#moduleFile_CdTe = os.path.join(baselinesfolder, 'baseline_modules_mass_US_CdTe.csv')


# In[ ]:


#residential system parameters
resi_sys1_size = 0.00552 #MW, first system on roof (degrades to 5 kW in 2024 after 9 years (2024-2015))
resi_sys1_deg = 1.1 #%/yr, corresponds to 20 yr life
resi_sys1_life = 20 #years of life
resi_sys1_life_repower = 9 #years of life but remove for repowering

resi_sys2_size = 0.0073 #MW, 2nd system on roof
resi_sys2_deg = 0.7 #%/yr, corresponds to 30 yr life
resi_sys2_life = 30 #years of life


# In[ ]:


#Residential case study
sim1.createScenario(name='Resi_keep', massmodulefile=moduleFile) #create the scenario, name and mod file attach
for mat in MATERIALS:
    materialfile = os.path.join(baselinesfolder, 'baseline_material_mass_'+str(mat)+'.csv')
    sim1.scenario['Resi_keep'].addMaterial(mat, massmatfile=materialfile) # add all materials listed in MATERIALS


# In[ ]:


#Residential case study
sim1.createScenario(name='Resi_repower', massmodulefile=moduleFile) #create the scenario, name and mod file attach
for mat in MATERIALS:
    materialfile = os.path.join(baselinesfolder, 'baseline_material_mass_'+str(mat)+'.csv')
    sim1.scenario['Resi_repower'].addMaterial(mat, massmatfile=materialfile) # add all materials listed in MATERIALS


# idx_temp = pd.RangeIndex(start=2024,stop=2051,step=1) #create the index
# CdTeRamp = pd.DataFrame(index=idx_temp, columns=['CdTe_deploy_[MWdc]'], dtype=float)
# CdTeRamp.loc[2024] = 14000
# CdTeRamp.loc[2030] = 50000#22000
# CdTeRamp_full = round(CdTeRamp.interpolate(),0)
# #CdTeRamp_full

# In[ ]:


#Modify the Scenario 
sim1.modifyScenario(scenarios='Resi_keep',stage='new_Installed_Capacity_[MW]', value=0)#, start_year=) #
#sim1.modifyScenario(scenarios='NAME',stage='new_Installed_Capacity_[MW]', value=0.005, start_year=2015) #5kW system installed in 2015
sim1.scenario['Resi_keep'].dataIn_m.loc[2015, 'new_Installed_Capacity_[MW]'] = resi_sys1_size
sim1.scenario['Resi_keep'].dataIn_m.loc[2015, 'mod_degradation'] = resi_sys1_deg
sim1.scenario['Resi_keep'].dataIn_m.loc[2015, 'mod_lifetime'] = resi_sys1_life


# In[ ]:


#Modify the Scenario 
sim1.modifyScenario(scenarios='Resi_repower',stage='new_Installed_Capacity_[MW]', value=0)#, start_year=) #
#sim1.modifyScenario(scenarios='NAME',stage='new_Installed_Capacity_[MW]', value=0.005, start_year=2015) #5kW system installed in 2015
sim1.scenario['Resi_repower'].dataIn_m.loc[2015, 'new_Installed_Capacity_[MW]'] = resi_sys1_size
sim1.scenario['Resi_repower'].dataIn_m.loc[2015, 'mod_degradation'] = resi_sys1_deg
sim1.scenario['Resi_repower'].dataIn_m.loc[2015, 'mod_lifetime'] = resi_sys1_life_repower

sim1.scenario['Resi_repower'].dataIn_m.loc[2024, 'new_Installed_Capacity_[MW]'] = resi_sys2_size
sim1.scenario['Resi_repower'].dataIn_m.loc[2024, 'mod_degradation'] = resi_sys2_deg
sim1.scenario['Resi_repower'].dataIn_m.loc[2024, 'mod_lifetime'] = resi_sys2_life


# In[ ]:


#do we also need a reuse scenario where both systems are used for full life? - wouldn't it just be additive?


# # Commercial Case Study
# This case study considers a set of commerical PV installations.

# In[ ]:





# In[ ]:





# In[ ]:





# # Utility Case Study
# This case study considers a set of utility scale PV installations.

# In[ ]:




