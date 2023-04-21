#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os,sys
from pathlib import Path
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 18})
plt.rcParams['figure.figsize'] = (8, 4)
cwd = os.getcwd() #grabs current working directory

supportMatfolder = str(Path().resolve().parent.parent.parent / 'PV_ICE' / 'baselines' / 'SupportingMaterial')
baselinesFolder = str(Path().resolve().parent.parent.parent / 'PV_ICE' / 'baselines')
carbonfolder = str(Path().resolve().parent.parent.parent / 'PV_ICE'/ 'baselines'/ 'CarbonLayer')


# In[2]:


#df = self.scenario[scen].dataOut_m
#df_in = self.scenario[scen].dataIn_m
#de = self.scenario[scen].dataOut_e
            
#pull in pickles
df = pd.read_pickle('dataOut_m.pkl')
df_in = pd.read_pickle('dataIn_m.pkl')
de = pd.read_pickle('dataOut_e.pkl')
de_in = pd.read_pickle('dataIn_e.pkl')


# In[ ]:





# In[27]:


gridemissionfactors = pd.read_csv(os.path.join(carbonfolder,'baseline_electricityemissionfactors.csv'))
materialprocesscarbon = pd.read_csv(os.path.join(carbonfolder,'baseline_materials_processCO2.csv'), index_col='Material')
countrygridmixes = pd.read_csv(os.path.join(carbonfolder, 'baseline_countrygridmix.csv'))
countrymodmfg = pd.read_csv(os.path.join(carbonfolder, 'baseline_module_countrymarketshare.csv'))


# In[4]:


#carbon intensity of country grid mixes
#extract lists
countryfuellist = [cols.split('_')[0] for cols in countrygridmixes.columns[1:]]
countrylist = (pd.DataFrame(countryfuellist)[0].unique()).tolist()
countryfuellist_fuels = [cols.split('_')[1] for cols in countrygridmixes.columns[1:]]
fuellist = (pd.DataFrame(countryfuellist_fuels)[0].unique()).tolist()

#create carbon intensity of country grid mix
final_country_carbon_int = []
for country in countrylist:
    temp_country_carbon = []
    for fuel in fuellist: 
        fuelemitfactor = gridemissionfactors[gridemissionfactors['Energy Source']==fuel]['CO2eq_kgpkWh_ember']
        fuelemitfactor = list(fuelemitfactor)[0]
        if str(country+'_'+fuel) in countrygridmixes:
            countryfuel = countrygridmixes[str(country+'_'+fuel)]
            temp_country_carbon.append(list(0.01*countryfuel*fuelemitfactor)) #multiply country fuel % by fuel factor
    final_country_carbon_int.append(list(pd.DataFrame(temp_country_carbon).sum())) #sum the carbon int by country

country_carbonpkwh = pd.DataFrame(final_country_carbon_int).T
country_carbonpkwh.columns = countrylist


# In[5]:


#carbon intensity of module manufacturing weighted by country
#list countries mfging modules
countriesmfgingmodules = list(countrymodmfg.columns[1:])

#weight carbon intensity of electricity by countries which mfging modules
countrycarbon_modmfg_co2eqpkwh = []
for country in countriesmfgingmodules:
    if country in country_carbonpkwh:
        currentcountry = country_carbonpkwh[country]*countrymodmfg[country]*.01
        countrycarbon_modmfg_co2eqpkwh.append(currentcountry)
    else: print(country)
        
modmfg_co2eqpkwh_bycountry = pd.DataFrame(countrycarbon_modmfg_co2eqpkwh).T #
modmfg_co2eqpkwh_bycountry['Global_kgCO2eqpkWh'] = modmfg_co2eqpkwh_bycountry.sum(axis=1) #annual carbon intensity of pv module mfg wtd by country


# In[6]:


#carbon impacts module mfging wtd by country
dc = modmfg_co2eqpkwh_bycountry.mul(de['mod_MFG'], axis=0)
dc.rename(columns={'Global_kgCO2eqpkWh':'Global'}, inplace=True)
dc = dc.add_suffix('_mod_MFG_kgCO2eq')


# In[7]:


#carbon impacts other module level steps
#assumption: all CO2 after mfg is attributable to target deployment country
country_deploy = 'USA' #user input in calc carbon function, default USA
dc['mod_Install_kgCO2eq'] = de['mod_Install']*country_carbonpkwh[country_deploy]
dc['mod_OandM_kgCO2eq'] = de['mod_OandM']*country_carbonpkwh[country_deploy]
dc['mod_Repair_kgCO2eq'] = de['mod_Repair']*country_carbonpkwh[country_deploy]
dc['mod_Demount_kgCO2eq'] = de['mod_Demount']*country_carbonpkwh[country_deploy]
dc['mod_Store_kgCO2eq'] = de['mod_Store']*country_carbonpkwh[country_deploy]
dc['mod_Resell_Certify_kgCO2eq'] = de['mod_Resell_Certify']*country_carbonpkwh[country_deploy]
dc['mod_ReMFG_Disassembly_kgCO2eq'] = de['mod_ReMFG_Disassembly']*country_carbonpkwh[country_deploy]
dc['mod_Recycle_Crush_kgCO2eq'] = de['mod_Recycle_Crush']*country_carbonpkwh[country_deploy]


# In[8]:


dc.head()


# # Material Level

# In[37]:


matEnergy = pd.read_pickle('matdataIn_e.pkl')
matMass = pd.read_pickle('matdataIn_m.pkl')
demat = pd.read_pickle('matdataOut_e.pkl')
dm = pd.read_pickle('matdataOut_m.pkl')

#e_mat_MFG_fuelfraction, e_mat_MFG
#e_mat_Recycled_HQ_fuelfraction


# In[10]:


countrymatmfg = pd.read_csv(os.path.join(carbonfolder, 'baseline_silicon_MFGing_countrymarketshare.csv'))
#countrymatmfg.head()
mat='silicon'


# In[11]:


country_carbonpkwh.columns


# In[12]:


#carbon intensity of material manufacturing weighted by country
#list countries mfging material
countriesmfgingmat = list(countrymatmfg.columns[1:])

#weight carbon intensity of electricity by countries which mfging modules
countrycarbon_matmfg_co2eqpkwh = []
for country in countriesmfgingmat:
    if country in country_carbonpkwh:
        currentcountry = country_carbonpkwh[country]*countrymatmfg[country]*.01
        countrycarbon_matmfg_co2eqpkwh.append(currentcountry)
    else: print(country)
        
matmfg_co2eqpkwh_bycountry = pd.DataFrame(countrycarbon_modmfg_co2eqpkwh).T #
matmfg_co2eqpkwh_bycountry['Global_kgCO2eqpkWh'] = modmfg_co2eqpkwh_bycountry.sum(axis=1) #annual carbon intensity of pv module mfg wtd by country


# In[13]:


#carbon impacts mat mfging wtd by country
#electric
dcmat = matmfg_co2eqpkwh_bycountry.mul((demat['mat_MFG_virgin']-demat['mat_MFG_virgin_fuel']),axis=0)
dcmat.rename(columns={'Global_kgCO2eqpkWh':'Global'}, inplace=True)
dcmat = dcmat.add_suffix('_vmfg_elec_kgCO2eq')

#fuel CO2 impacts
steamHeat = list(gridemissionfactors[gridemissionfactors['Energy Source']=='SteamAndHeat']['CO2_kgpkWh_EPA'])[0]
dcmat['mat_MFG_virgin_fuel_CO2eq'] = demat['mat_MFG_virgin_fuel']*steamHeat #CO2 from mfging fuels
dcmat['mat_MFGScrap_HQ_fuel_CO2eq'] = demat['mat_MFGScrap_HQ_fuel']*steamHeat #CO2 from recycling fuels


# In[14]:


dcmat


# In[45]:


#CO2 process emissions from MFGing (v, lq, hq)
#mass of material being processed in each stream * CO2 intensity of that process
dcmat['mat_vMFG_CO2eq'] = dm['mat_Virgin_Stock']*materialprocesscarbon.loc[mat,'v_MFG_kgCO2eqpkg']
dcmat['mat_LQmfg_CO2eq'] = dm['mat_MFG_Scrap_Sentto_Recycling']*materialprocesscarbon.loc[mat,'LQ_Recycle_kgCO2eqpkg']
dcmat['mat_LQeol_CO2eq'] = dm['mat_recycled_target']*materialprocesscarbon.loc[mat,'LQ_Recycle_kgCO2eqpkg']
dcmat['mat_LQ_CO2eq'] = dcmat['mat_LQmfg_CO2eq']+dcmat['mat_LQeol_CO2eq']
dcmat['mat_HQmfg_CO2eq'] = dm['mat_MFG_Recycled_into_HQ']*materialprocesscarbon.loc[mat,'HQ_Recycle_kgCO2eqpkg']
dcmat['mat_HQeol_CO2eq'] = dm['mat_EOL_Recycled_2_HQ']*materialprocesscarbon.loc[mat,'HQ_Recycle_kgCO2eqpkg']
dcmat['mat_HQ_CO2eq'] = dcmat['mat_HQmfg_CO2eq']+dcmat['mat_HQeol_CO2eq'] 


# In[46]:


dcmat


# In[ ]:




