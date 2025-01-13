#!/usr/bin/env python
# coding: utf-8

# # SIPS: QUIP SERIES
# This journal explores the case studies of the SIPS 2025 project understanding the implications of repowering and module reuse. This compliments analyses conducted in SAM and PV Watts. Below are the Residential, Commercial, and Utility scale case studies

# In[1]:


#setup
import numpy as np
import pandas as pd
import os,sys
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.express as px

import PV_ICE

cwd = os.getcwd() #grabs current working directory

testfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'TEMP' / 'SIPS-Repowering')
#inputfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines'/'NRELStdScenarios')
baselinesfolder = str(Path().resolve().parent.parent /'PV_ICE' / 'baselines')
supportMatfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines' / 'SupportingMaterial')
#altBaselinesfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines' / 'Energy_CellModuleTechCompare')

if not os.path.exists(testfolder):
    os.makedirs(testfolder)

print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("pyplot ", plt.matplotlib.__version__)
print("PV_ICE version ", PV_ICE.__version__)


# In[2]:


sim1 = PV_ICE.Simulation(name='SIPS', path=testfolder)


# ## Residential Case Study
# This case study considers a residential system where the PV system is not at technical end of life (installed 2015), but the roof needs replacing in 2024. The owner has the option of keeping the old system or replacing the PV system.

# In[3]:


#c-Si
MATERIALS = ['glass','aluminium_frames','silver','silicon', 'copper', 'encapsulant', 'backsheet']
moduleFile_m = os.path.join(baselinesfolder, 'baseline_modules_mass_US_updatedT50T90.csv')
moduleFile_e = os.path.join(baselinesfolder, 'baseline_modules_energy.csv')

#CdTe
#MATERIALS_CdTe = ['glass_cdte','aluminium_frames_cdte', 'copper_cdte', 'encapsulant_cdte','cadmium','tellurium']
#moduleFile_CdTe = os.path.join(baselinesfolder, 'baseline_modules_mass_US_CdTe.csv')


# In[4]:


#residential system parameters
resi_sys1_size = 0.00552 #MW, first system on roof (degrades to 5 kW in 2024 after 9 years (2024-2015))
resi_sys1_deg = 1.1 #%/yr, corresponds to 20 yr life
resi_sys1_life = 20 #years of life
resi_sys1_life_repower = 9 #years of life but remove for repowering
resi_sys1_eff = 19.02 #from SAM, PV ICE 2015 eff = 17%

resi_sys2_size = 0.0073 #MW, 2nd system on roof
resi_sys2_deg = 0.7 #%/yr, corresponds to 30 yr life
resi_sys2_life = 30 #years of life
resi_sys2_eff = 20.57 #from SAM, PV ICE 2024 eff = 22.4%


# In[5]:


#Residential case study
sim1.createScenario(name='Resi_keep', massmodulefile=moduleFile_m, energymodulefile=moduleFile_e) #create the scenario, name and mod file attach
for mat in MATERIALS:
    materialfile_m = os.path.join(baselinesfolder, 'baseline_material_mass_'+str(mat)+'.csv')
    materialfile_e = os.path.join(baselinesfolder, 'baseline_material_energy_'+str(mat)+'.csv')
    sim1.scenario['Resi_keep'].addMaterial(mat, massmatfile=materialfile_m, energymatfile=materialfile_e) # add all materials listed in MATERIALS


# In[6]:


#Residential case study
sim1.createScenario(name='Resi_repower', massmodulefile=moduleFile_m, energymodulefile=moduleFile_e) #create the scenario, name and mod file attach
for mat in MATERIALS:
    materialfile_m = os.path.join(baselinesfolder, 'baseline_material_mass_'+str(mat)+'.csv')
    materialfile_e = os.path.join(baselinesfolder, 'baseline_material_energy_'+str(mat)+'.csv')
    sim1.scenario['Resi_repower'].addMaterial(mat, massmatfile=materialfile_m, energymatfile=materialfile_e) # add all materials listed in MATERIALS


# idx_temp = pd.RangeIndex(start=2024,stop=2051,step=1) #create the index
# CdTeRamp = pd.DataFrame(index=idx_temp, columns=['CdTe_deploy_[MWdc]'], dtype=float)
# CdTeRamp.loc[2024] = 14000
# CdTeRamp.loc[2030] = 50000#22000
# CdTeRamp_full = round(CdTeRamp.interpolate(),0)
# #CdTeRamp_full

# In[7]:


#Modify the Scenario 
sim1.modifyScenario(scenarios='Resi_keep',stage='new_Installed_Capacity_[MW]', value=0, start_year=1995) #
#sim1.modifyScenario(scenarios='NAME',stage='new_Installed_Capacity_[MW]', value=0.005, start_year=2015) #5kW system installed in 2015
sim1.scenario['Resi_keep'].dataIn_m.loc[2015-1995, 'new_Installed_Capacity_[MW]'] = resi_sys1_size
sim1.scenario['Resi_keep'].dataIn_m.loc[2015-1995, 'mod_degradation'] = resi_sys1_deg
sim1.scenario['Resi_keep'].dataIn_m.loc[2015-1995, 'mod_lifetime'] = resi_sys1_life
sim1.scenario['Resi_keep'].dataIn_m.loc[2015-1995, 'mod_eff'] = resi_sys1_eff


# In[8]:


#Modify the Scenario 
sim1.modifyScenario(scenarios='Resi_repower',stage='new_Installed_Capacity_[MW]', value=0, start_year=1995) #
#sim1.modifyScenario(scenarios='NAME',stage='new_Installed_Capacity_[MW]', value=0.005, start_year=2015) #5kW system installed in 2015
sim1.scenario['Resi_repower'].dataIn_m.loc[2015-1995, 'new_Installed_Capacity_[MW]'] = resi_sys1_size
sim1.scenario['Resi_repower'].dataIn_m.loc[2015-1995, 'mod_degradation'] = resi_sys1_deg
sim1.scenario['Resi_repower'].dataIn_m.loc[2015-1995, 'mod_lifetime'] = resi_sys1_life_repower
sim1.scenario['Resi_repower'].dataIn_m.loc[2015-1995, 'mod_eff'] = resi_sys1_eff

sim1.scenario['Resi_repower'].dataIn_m.loc[2024-1995, 'new_Installed_Capacity_[MW]'] = resi_sys2_size
sim1.scenario['Resi_repower'].dataIn_m.loc[2024-1995, 'mod_degradation'] = resi_sys2_deg
sim1.scenario['Resi_repower'].dataIn_m.loc[2024-1995, 'mod_lifetime'] = resi_sys2_life
sim1.scenario['Resi_repower'].dataIn_m.loc[2024-1995, 'mod_eff'] = resi_sys2_eff


# In[9]:


#extend the analysis period for full energy calc
sim1.trim_Years(2010,2060)


# In[10]:


#do we also need a reuse scenario where both systems are used for full life? - wouldn't it just be additive?


# In[11]:


plt.plot(sim1.scenario['Resi_keep'].dataIn_m.loc[:, 'year'], 
         sim1.scenario['Resi_keep'].dataIn_m.loc[:, 'new_Installed_Capacity_[MW]'])
plt.plot(sim1.scenario['Resi_repower'].dataIn_m.loc[:, 'year'], 
         sim1.scenario['Resi_repower'].dataIn_m.loc[:, 'new_Installed_Capacity_[MW]'], ls='--')
plt.ylim(0,0.01)
plt.ylabel('Deployed [MW_dc]')
plt.legend(['Keep','Repower'])


# In[12]:


sim1.calculateFlows()


# In[13]:


sim1_yearly, sim1_cumu = sim1.aggregateResults()
sim1_allenergy, sim1_energyGen, sim1_energyDemands_all = sim1.aggregateEnergyResults()


# In[14]:


decommisioned = sim1_yearly.filter(like='Decommisioned')
plt.plot(decommisioned*1000)
plt.legend(['Keep','Repower'])
plt.ylim(0,14)
plt.ylabel('Decommissioned Capacity [kW_dc]')


# In[15]:


plt.plot(sim1_energyGen/1e6)
plt.legend(['Keep','Repower'])
plt.ylim(0,12.0)
plt.ylabel('Annual Energy Generation [MWh]')


# In[16]:


cumu_energy_gen = sim1_energyGen.cumsum().loc[[2060]]
cumu_energy_gen_MWh = cumu_energy_gen/1e6
cumu_energy_gen_MWh.columns = ['Keep', 'Repower']
cumu_energy_gen_MWh.index=['Energy Gen [MWh]']
cumu_energy_gen_MWh


# In[17]:


#sum the energy demands
energydemand_keep = sim1_energyDemands_all.filter(like='keep').sum(axis=1).sum()/1e6 #MWh
energydemand_repower = sim1_energyDemands_all.filter(like='repower').sum(axis=1).sum()/1e6 #MWh


# In[18]:


cumu_energy_MWh = cumu_energy_gen_MWh.copy()
cumu_energy_MWh.loc['Energy Demand [MWh]','Keep'] = energydemand_keep
cumu_energy_MWh.loc['Energy Demand [MWh]','Repower'] = energydemand_repower
cumu_energy_MWh


# In[19]:


#EROI
cumu_energy_MWh.loc['EROI'] = cumu_energy_MWh.loc['Energy Gen [MWh]']/cumu_energy_MWh.loc['Energy Demand [MWh]']
cumu_energy_MWh


# In[20]:


#material demands
modmass_keep = sim1_yearly.loc[2015,'VirginStock_Module_SIPS_Resi_keep_[Tonnes]']
modmass_repower = sim1_yearly.loc[:,'VirginStock_Module_SIPS_Resi_repower_[Tonnes]'].sum()


# In[21]:


#wastes
modwaste_keep = sim1_cumu.iloc[-1]['WasteAll_Module_SIPS_Resi_keep_[Tonnes]']
modwaste_repower = sim1_cumu.iloc[-1]['WasteAll_Module_SIPS_Resi_repower_[Tonnes]']


# In[22]:


plt.plot(sim1_yearly.loc[:,'VirginStock_Module_SIPS_Resi_keep_[Tonnes]'], label = 'matdemand_keep')
plt.plot(sim1_yearly.loc[:,'VirginStock_Module_SIPS_Resi_repower_[Tonnes]'], ls='--', label = 'matdemand_repower')

plt.plot(sim1_yearly.loc[:,'WasteAll_Module_SIPS_Resi_keep_[Tonnes]'], label = 'waste_keep')
plt.plot(sim1_yearly.loc[:,'WasteAll_Module_SIPS_Resi_repower_[Tonnes]'], ls='--', label='waste_repower')

plt.ylim(0,0.5)
plt.ylabel('Material Demand and Wastes [tonnes]')
plt.legend()


# In[23]:


cumu_metrics = cumu_energy_MWh.copy()
cumu_metrics.loc['Virgin Material Demands [tonnes]','Keep'] = modmass_keep
cumu_metrics.loc['Virgin Material Demands [tonnes]','Repower'] = modmass_repower
cumu_metrics.loc['Wastes [tonnes]', 'Keep'] = modwaste_keep
cumu_metrics.loc['Wastes [tonnes]', 'Repower'] = modwaste_repower

round(cumu_metrics,2)


# In[24]:


sim1.calculateCarbonFlows()


# In[25]:


sim1.scenario['Resi_keep'].dataOut_c.head(60) 
#nans are expected becuase the default files are 2000-2100, and this scenarios is 2010 to 2060


# # Commercial Case Study
# This case study considers a set of commerical PV installations.

# In[ ]:





# In[ ]:





# In[ ]:





# # Utility Case Study
# This case study considers a set of utility scale PV installations.

# In[ ]:




