#!/usr/bin/env python
# coding: utf-8

# # ReEDS Scenarios on PV ICE Tool

# To explore different scenarios for furture installation projections of PV (or any technology), ReEDS output data can be useful in providing standard scenarios. ReEDS installation projections are used in this journal as input data to the PV ICE tool. 
# 
# Current sections include:
# 
# <ol>
#     <li> ### Reading a standard ReEDS output file and saving it in a PV ICE input format </li>
# <li>### Reading scenarios of interest and running PV ICE tool </li>
# <li>###Plotting </li>
# <li>### GeoPlotting.</li>
# </ol>
#     Notes:
#    
# Scenarios of Interest:
# 	the Ref.Mod, 
# o	95-by-35.Adv, and 
# o	95-by-35+Elec.Adv+DR ones
# 

# In[1]:


import numpy as np
import pandas as pd
import os,sys
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})
plt.rcParams['figure.figsize'] = (12, 8)


# In[2]:


import os
from pathlib import Path

testfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'TEMP')

print ("Your simulation will be stored in %s" % testfolder)


# # Reading a standard ReEDS output file and saving it in a PV ICE input format

# In[3]:


reedsFile = str(Path().resolve().parent.parent.parent / 'December Core Scenarios ReEDS Outputs Solar Futures v2a.xlsx')
print ("Input file is stored in %s" % reedsFile)


# In[4]:


rawdf = pd.read_excel(reedsFile,
                        sheet_name="UPV Capacity (GW)")
                        #index_col=[0,2,3]) #this casts scenario, PCA and State as levels
#now set year as an index in place
rawdf.drop(columns=['State'], inplace=True)
rawdf.drop(columns=['Tech'], inplace=True)
rawdf.set_index(['Scenario','Year','PCA'], inplace=True)


# In[5]:


rawdf.head()


# In[6]:


scenarios = list(rawdf.index.get_level_values('Scenario').unique())
PCAs = list(rawdf.index.get_level_values('PCA').unique())
scenarios


# In[7]:


import PV_ICE
r1 = PV_ICE.Simulation(name='Simulation1', path=testfolder)
r1.createScenario(name='US', file=r'..\baselines\baseline_modules_US.csv')
baseline = r1.scenario['US'].data
baseline = baseline.drop(columns=['new_Installed_Capacity_[MW]'])
baseline.set_index('year', inplace=True)
baseline.index = pd.PeriodIndex(baseline.index, freq='A')  # A -- Annual
baseline.head()


# In[8]:


rawdf.head(21)


# In[9]:


r'''
A = rawdf.unstack(level=1).iloc[0]
A = A.droplevel(level=0)
A.name = 'new_Installed_Capacity_[MW]'
A = pd.DataFrame(A)
A.index=pd.PeriodIndex(A.index, freq='A')
A = A.resample('Y').asfreq()
A = A['new_Installed_Capacity_[MW]'].fillna(0).groupby(A['new_Installed_Capacity_[MW]'].notna().cumsum()).transform('mean')    
A = pd.DataFrame(A)
A['new_Installed_Capacity_[MW]'] = A['new_Installed_Capacity_[MW]'] * 1000   # ReEDS file is in GW.
# Add other columns
A = pd.concat([A, baseline.reindex(A.index)], axis=1)
A.loc['2050']['new_Installed_Capacity_[MW]'] = A.loc['2050']['new_Installed_Capacity_[MW]']/2   # Dividing last value by 2
new_row = A[-1:]
new_row.index = new_row.index.shift(periods=1)   #Shifting so new row is 2051
A = pd.concat([A,pd.concat([new_row])])              
A.index = A.index.shift(periods=-1)          # Shifting back so it goes from 2009-2050
'''
pass


# In[10]:


for ii in range (len(rawdf.unstack(level=1))):
    PCA = rawdf.unstack(level=1).iloc[ii].name[1]
    SCEN = rawdf.unstack(level=1).iloc[ii].name[0]
    SCEN=SCEN.replace('+', '_')
    filetitle = SCEN+'_'+PCA +'.csv'
    filetitle = os.path.join(testfolder, 'PCAs', filetitle)
    A = rawdf.unstack(level=1).iloc[ii]
    A = A.droplevel(level=0)
    A.name = 'new_Installed_Capacity_[MW]'
    A = pd.DataFrame(A)
    A.index=pd.PeriodIndex(A.index, freq='A')
    A = A.resample('Y').asfreq()
    A = A['new_Installed_Capacity_[MW]'].fillna(0).groupby(A['new_Installed_Capacity_[MW]'].notna().cumsum()).transform('mean')    
    A = pd.DataFrame(A)
    A['new_Installed_Capacity_[MW]'] = A['new_Installed_Capacity_[MW]'] * 1000   # ReEDS file is in GW.
    # Add other columns
    A = pd.concat([A, baseline.reindex(A.index)], axis=1)
    A.loc['2050']['new_Installed_Capacity_[MW]'] = A.loc['2050']['new_Installed_Capacity_[MW]']/2   # Dividing last value by 2
    new_row = A[-1:]
    new_row.index = new_row.index.shift(periods=1)   #Shifting so new row is 2051
    A = pd.concat([A,pd.concat([new_row])])              
    A.index = A.index.shift(periods=-1)          # Shifting back so it goes from 2009-2050

    
    header = "year,new_Installed_Capacity_[MW],mod_eff,mod_reliability_t50,mod_reliability_t90,"    "mod_degradation,mod_lifetime,mod_MFG_eff,mod_EOL_collection_eff,mod_EOL_collected_recycled,"    "mod_Repowering,mod_Repairing\n"    "year,MW,%,years,years,%,years,%,%,%,%,%\n"

    with open(filetitle, 'w', newline='') as ict:
    # Write the header lines, including the index variable for
    # the last one if you're letting Pandas produce that for you.
    # (see above).
        for line in header:
            ict.write(line)

        #    savedata.to_csv(ict, index=False)
        A.to_csv(ict, header=False)


# ## Save Input Files By States

# In[179]:


rawdf = pd.read_excel(reedsFile,
                        sheet_name="UPV Capacity (GW)")
                        #index_col=[0,2,3]) #this casts scenario, PCA and State as levels
#now set year as an index in place
#rawdf.drop(columns=['State'], inplace=True)
rawdf.drop(columns=['Tech'], inplace=True)
rawdf.set_index(['Scenario','Year','PCA', 'State'], inplace=True)
rawdf.head(21)


# In[180]:


df = rawdf.groupby(['Scenario','State', 'Year'])['Capacity (GW)'].sum(axis=0)
df = pd.DataFrame(df)


# In[181]:


import PV_ICE
r1 = PV_ICE.Simulation(name='Simulation1', path=testfolder)
r1.createScenario(name='US', file=r'..\baselines\baseline_modules_US.csv')
baseline = r1.scenario['US'].data
baseline = baseline.drop(columns=['new_Installed_Capacity_[MW]'])
baseline.set_index('year', inplace=True)
baseline.index = pd.PeriodIndex(baseline.index, freq='A')  # A -- Annual
baseline.head()


# In[182]:


for ii in range (len(df.unstack(level=2))):
    STATE = df.unstack(level=2).iloc[ii].name[1]
    SCEN = df.unstack(level=2).iloc[ii].name[0]
    SCEN=SCEN.replace('+', '_')
    filetitle = SCEN+'_'+STATE +'.csv'
    filetitle = os.path.join(testfolder, 'STATEs', filetitle)
    A = df.unstack(level=2).iloc[ii]
    A = A.droplevel(level=0)
    A.name = 'new_Installed_Capacity_[MW]'
    A = pd.DataFrame(A)
    A.index=pd.PeriodIndex(A.index, freq='A')
    A = A.resample('Y').asfreq()
    A = A['new_Installed_Capacity_[MW]'].fillna(0).groupby(A['new_Installed_Capacity_[MW]'].notna().cumsum()).transform('mean')    
    A = pd.DataFrame(A)
    A['new_Installed_Capacity_[MW]'] = A['new_Installed_Capacity_[MW]'] * 1000   # ReEDS file is in GW.
    # Add other columns
    A = pd.concat([A, baseline.reindex(A.index)], axis=1)
    A.loc['2050']['new_Installed_Capacity_[MW]'] = A.loc['2050']['new_Installed_Capacity_[MW]']/2   # Dividing last value by 2
    new_row = A[-1:]
    new_row.index = new_row.index.shift(periods=1)   #Shifting so new row is 2051
    A = pd.concat([A,pd.concat([new_row])])              
    A.index = A.index.shift(periods=-1)          # Shifting back so it goes from 2009-2050

    
    header = "year,new_Installed_Capacity_[MW],mod_eff,mod_reliability_t50,mod_reliability_t90,"    "mod_degradation,mod_lifetime,mod_MFG_eff,mod_EOL_collection_eff,mod_EOL_collected_recycled,"    "mod_Repowering,mod_Repairing\n"    "year,MW,%,years,years,%,years,%,%,%,%,%\n"

    with open(filetitle, 'w', newline='') as ict:
    # Write the header lines, including the index variable for
    # the last one if you're letting Pandas produce that for you.
    # (see above).
        for line in header:
            ict.write(line)

        #    savedata.to_csv(ict, index=False)
        A.to_csv(ict, header=False)


# ### ATTEMPT 2

# In[183]:


df = pd.read_excel(reedsFile,
                        sheet_name="UPV Capacity (GW)")
                        #index_col=[0,2,3]) #this casts scenario, PCA and State as levels
df.drop(columns=['Tech'], inplace=True)


# In[184]:


#foo = df.pivot_table(index=['Scenario','Year'],columns='State',aggfunc=sum)
foo = df.pivot_table(index=['Scenario','State'],columns='Year',aggfunc=sum)

foo = pd.DataFrame(foo)
foo.head()


# In[199]:


for ii in range (len(foo)):
    STATE = foo.index[ii][1]
    SCEN = foo.index[ii][0]
    SCEN=SCEN.replace('+', '_')
    filetitle = SCEN+'_'+STATE +'.csv'
    filetitle = os.path.join(testfolder, 'STATEs', filetitle)
    A = pd.DataFrame(foo.iloc[ii])
    #A = A.unstack(level=0).iloc[ii]
    A = A.droplevel(level=0)
    A.columns = [' '.join(col).strip() for col in A.columns.values]
    A.rename(columns = {list(A)[0]: 'new_Installed_Capacity_[MW]'}, inplace = True)
    A.index=pd.PeriodIndex(A.index, freq='A')
    A = A.resample('Y').asfreq()
    A = A['new_Installed_Capacity_[MW]'].fillna(0).groupby(A['new_Installed_Capacity_[MW]'].notna().cumsum()).transform('mean')    
    A = pd.DataFrame(A)
    A['new_Installed_Capacity_[MW]'] = A['new_Installed_Capacity_[MW]'] * 1000   # ReEDS file is in GW.
    # Add other columns
    A = pd.concat([A, baseline.reindex(A.index)], axis=1)
    A.loc['2050']['new_Installed_Capacity_[MW]'] = A.loc['2050']['new_Installed_Capacity_[MW]']/2   # Dividing last value by 2
    new_row = A[-1:]
    new_row.index = new_row.index.shift(periods=1)   #Shifting so new row is 2051
    A = pd.concat([A,pd.concat([new_row])])              
    A.index = A.index.shift(periods=-1)          # Shifting back so it goes from 2009-2050

    header = "year,new_Installed_Capacity_[MW],mod_eff,mod_reliability_t50,mod_reliability_t90,"    "mod_degradation,mod_lifetime,mod_MFG_eff,mod_EOL_collection_eff,mod_EOL_collected_recycled,"    "mod_Repowering,mod_Repairing\n"    "year,MW,%,years,years,%,years,%,%,%,%,%\n"

    with open(filetitle, 'w', newline='') as ict:
    # Write the header lines, including the index variable for
    # the last one if you're letting Pandas produce that for you.
    # (see above).
        for line in header:
            ict.write(line)

        #    savedata.to_csv(ict, index=False)
        A.to_csv(ict, header=False)


# ### Reading GIS inputs

# In[190]:


GISfile = str(Path().resolve().parent.parent.parent / 'gis_centroid_n.xlsx')
GIS = pd.read_excel(GISfile)
GIS = GIS.set_index('id')


# In[191]:


GIS.head()


# In[192]:


GIS.loc['p1'].long


# ### Create Scenarios

# In[193]:


simulationname = scenarios
simulationname = [w.replace('+', '_') for w in simulationname]
PCA = PCAs[0]
simulationname


# In[194]:


SFscenarios = [scenarios[0], scenarios[4], scenarios[8]]
SFscenarios


# In[195]:


#for ii in range (0, 1): #len(scenarios):
r1 = PV_ICE.Simulation(name=SFscenarios[0], path=testfolder)
for jj in range (0, len(PCAs)): 
    filetitle = SFscenarios[0]+'_'+PCAs[jj]+'.csv'
    filetitle = os.path.join(testfolder, 'PCAs', filetitle)        
    r1.createScenario(name=PCAs[jj], file=filetitle)
    r1.scenario[PCAs[jj]].addMaterial('glass', file=r'..\baselines\ReedsSubset\baseline_material_glass_Reeds.csv')
    r1.scenario[PCAs[jj]].addMaterial('silicon', file=r'..\baselines\ReedsSubset\baseline_material_silicon_Reeds.csv')
    r1.scenario[PCAs[jj]].addMaterial('silver', file=r'..\baselines\ReedsSubset\baseline_material_silver_Reeds.csv')
    r1.scenario[PCAs[jj]].addMaterial('copper', file=r'..\baselines\ReedsSubset\baseline_material_copper_Reeds.csv')
    r1.scenario[PCAs[jj]].addMaterial('aluminum', file=r'..\baselines\ReedsSubset\baseline_material_aluminium_Reeds.csv')
    r1.scenario[PCAs[jj]].latitude = GIS.loc[PCAs[jj]].lat
    r1.scenario[PCAs[jj]].longitude = GIS.loc[PCAs[jj]].long

r2 = PV_ICE.Simulation(name=SFscenarios[1], path=testfolder)
for jj in range (0, len(PCAs)): 
    filetitle = SFscenarios[1]+'_'+PCAs[jj]+'.csv'
    filetitle = os.path.join(testfolder, 'PCAs', filetitle)        
    r2.createScenario(name=PCAs[jj], file=filetitle)
    r2.scenario[PCAs[jj]].addMaterial('glass', file=r'..\baselines\ReedsSubset\baseline_material_glass_Reeds.csv')
    r2.scenario[PCAs[jj]].addMaterial('silicon', file=r'..\baselines\ReedsSubset\baseline_material_silicon_Reeds.csv')
    r2.scenario[PCAs[jj]].addMaterial('silver', file=r'..\baselines\ReedsSubset\baseline_material_silver_Reeds.csv')
    r2.scenario[PCAs[jj]].addMaterial('copper', file=r'..\baselines\ReedsSubset\baseline_material_copper_Reeds.csv')
    r2.scenario[PCAs[jj]].addMaterial('aluminum', file=r'..\baselines\ReedsSubset\baseline_material_aluminium_Reeds.csv')
    r2.scenario[PCAs[jj]].latitude = GIS.loc[PCAs[jj]].lat
    r2.scenario[PCAs[jj]].longitude = GIS.loc[PCAs[jj]].long

r3 = PV_ICE.Simulation(name=SFscenarios[2], path=testfolder)
for jj in range (0, len(PCAs)): 
    filetitle = simulationname[8]+'_'+PCAs[jj]+'.csv'
    filetitle = os.path.join(testfolder, 'PCAs', filetitle)        
    r3.createScenario(name=PCAs[jj], file=filetitle)
    r3.scenario[PCAs[jj]].addMaterial('glass', file=r'..\baselines\ReedsSubset\baseline_material_glass_Reeds.csv')
    r3.scenario[PCAs[jj]].addMaterial('silicon', file=r'..\baselines\ReedsSubset\baseline_material_silicon_Reeds.csv')
    r3.scenario[PCAs[jj]].addMaterial('silver', file=r'..\baselines\ReedsSubset\baseline_material_silver_Reeds.csv')
    r3.scenario[PCAs[jj]].addMaterial('copper', file=r'..\baselines\ReedsSubset\baseline_material_copper_Reeds.csv')
    r3.scenario[PCAs[jj]].addMaterial('aluminum', file=r'..\baselines\ReedsSubset\baseline_material_aluminium_Reeds.csv')
    r3.scenario[PCAs[jj]].latitude = GIS.loc[PCAs[jj]].lat
    r3.scenario[PCAs[jj]].longitude = GIS.loc[PCAs[jj]].long


# In[196]:


r1.calculateMassFlow()
r2.calculateMassFlow()
r3.calculateMassFlow()


# In[198]:


print("PCAs:", r1.scenario.keys())
print("Module Keys:", r1.scenario[PCAs[jj]].data.keys())
print("Material Keys: ", r1.scenario[PCAs[jj]].material['glass'].materialdata.keys())


# In[197]:


r1.scenario['p1'].data.head()


# In[43]:


keyword='new_Installed_Capacity_[MW]'
foo = r1.scenario[PCAs[0]].data[keyword].copy()
plt.figure()
plt.plot(r1.scenario[PCAs[0]].data['year'], foo, label=PCAs[12])
plt.title(keyword)
plt.legend()

for jj in range (1, len(PCAs)): 
    foo += r1.scenario[PCAs[jj]].data[keyword]
     
fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)
ax.plot(r1.scenario[PCAs[0]].data['year'], foo, label='US')
plt.title("Cumulative" +keyword)
#ax.set_yscale('log')
print(max(foo))


# In[ ]:


df.to_csv(r'Path where you want to store the exported CSV file\File Name.csv')


# In[ ]:





# In[ ]:





# In[ ]:





# In[40]:


r1.plotScenariosComparison(keyword='Cumulative_Area_disposedby_Failure')


# In[41]:


r1.plotMaterialComparisonAcrossScenarios(material='silicon', keyword='mat_Total_Landfilled')


# In[61]:


keyword='mat_Total_Landfilled'
plt.figure()
plt.plot(r1.scenario[PCAs[0]].data['year'], foo, label=PCAs[12])
plt.title(keyword)
plt.legend()

for jj in range (1, len(PCAs)): 
    foo['silver'] += r1.scenario[PCAs[jj]].material['silver'].materialdata[keyword]


fig = plt.figure()
ax = fig.add_subplot(2, 1, 1)
ax.plot(r1.scenario[PCAs[0]].data['year'], foo['silver'], label='US')
plt.title("Material Landfilled per Year US")
#ax.set_yscale('log')
print(max(foo))


# In[ ]:





# In[60]:


foo = r1.scenario[PCAs[0]].material['silver'].materialdata[keyword].copy()
foo = r1.scenario[PCAs[0]].material['silver'].materialdata[keyword].copy()
foo = foo.to_frame(name='silver')
UScum=pd.DataFrame()
UScum['silver'] = foo['silver']


# ## Adding Material Landfilled for the US 

# In[90]:


keyword='mat_Total_Landfilled'
materials = ['glass', 'silicon', 'silver', 'copper', 'aluminum']

USyearly=pd.DataFrame()


for ii in range (0, len(materials)):    
    material = materials[ii]
    foo = r1.scenario[PCAs[0]].material[material].materialdata[keyword].copy()
    foo = r1.scenario[PCAs[0]].material[material].materialdata[keyword].copy()
    foo = foo.to_frame(name=material)
    USyearly[material] = foo[material]

    for jj in range (1, len(PCAs)): 
        USyearly[material] += r1.scenario[PCAs[jj]].material[material].materialdata[keyword]

USyearly = USyearly/907185
USyearly.head()


# In[91]:


plt.plot([],[],color='m', label='glass', linewidth=5)
plt.plot([],[],color='c', label='silicon', linewidth=5)
plt.plot([],[],color='r', label='silver', linewidth=5)
plt.plot([],[],color='k', label='copper', linewidth=5)
plt.plot([],[],color='g', label='aluminum', linewidth=5)

plt.stackplot(r1.scenario[PCAs[0]].data['year'], USyearly['glass'], USyearly['silicon'], USyearly['silver'], USyearly['copper'], USyearly['aluminum'], colors=['m','c','r','k', 'g'])
plt.ylabel('Mass [Tons]')
plt.xlim([2010, 2050])
plt.title('Yearly')
plt.legend(materials)


# In[112]:


keyword='mat_Virgin_Stock'
materials = ['glass', 'silicon', 'silver', 'copper', 'aluminum']

USyearly=pd.DataFrame()


for ii in range (0, len(materials)):    
    material = materials[ii]
    foo = r1.scenario[PCAs[0]].material[material].materialdata[keyword].copy()
    foo = r1.scenario[PCAs[0]].material[material].materialdata[keyword].copy()
    foo = foo.to_frame(name=material)
    USyearly[material] = foo[material]

    for jj in range (1, len(PCAs)): 
        USyearly[material] += r1.scenario[PCAs[jj]].material[material].materialdata[keyword]

USyearly = USyearly/907185
USyearly.head()


plt.plot([],[],color='m', label='glass', linewidth=5)
plt.plot([],[],color='c', label='silicon', linewidth=5)
plt.plot([],[],color='r', label='silver', linewidth=5)
plt.plot([],[],color='k', label='copper', linewidth=5)
plt.plot([],[],color='g', label='aluminum', linewidth=5)

plt.stackplot(r1.scenario[PCAs[0]].data['year'], USyearly['glass'], USyearly['silicon'], USyearly['silver'], USyearly['copper'], USyearly['aluminum'], colors=['m','c','r','k', 'g'])
plt.ylabel('Mass [Tons]')
plt.xlim([2010, 2050])
plt.title(keyword)
plt.legend(materials)


# In[ ]:





# ## Calculating Cumulative Yearly Waste for US

# In[114]:


UScum = USyearly.copy()
UScum = UScum.cumsum()
UScum.head()

    
plt.plot([],[],color='m', label='glass', linewidth=5)
plt.plot([],[],color='c', label='silicon', linewidth=5)
plt.plot([],[],color='r', label='silver', linewidth=5)
plt.plot([],[],color='k', label='copper', linewidth=5)
plt.plot([],[],color='g', label='aluminum', linewidth=5)

plt.stackplot(r1.scenario[PCAs[0]].data['year'], UScum['glass'], UScum['silicon'], UScum['silver'], UScum['copper'], UScum['aluminum'], colors=['m','c','r','k', 'g'])
plt.ylabel('Mass [Tons]')
plt.xlim([2010, 2050])
plt.title('Cumulative')
plt.legend(materials)

plt.figure()
plt.stackplot(r1.scenario[PCAs[0]].data['year'], UScum['glass'], UScum['silicon'], UScum['silver'], UScum['copper'], UScum['aluminum'], colors=['m','c','r','k', 'g'])
plt.ylabel('Mass [Tons]')
plt.title('Cumulative')
plt.xlim([2010, 2050])
plt.yscale('log')
plt.legend(materials)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ## Non stacked plot, previuos method

# In[100]:


''' 
material1='glass'
material2='silicon'
material3='silver'
keyword='mat_Total_Landfilled'

USlandfill_glass = r1.scenario[PCAs[0]].material[material1].materialdata[keyword]
USlandfill_silicon = r1.scenario[PCAs[0]].material[material2].materialdata[keyword]
USlandfill_silver = r1.scenario[PCAs[0]].material[material3].materialdata[keyword]

for jj in range (1, len(PCAs)): 
    USlandfill_glass += r1.scenario[PCAs[jj]].material[material1].materialdata[keyword] 
    USlandfill_silicon += r1.scenario[PCAs[jj]].material[material2].materialdata[keyword] 
    USlandfill_silver += r1.scenario[PCAs[jj]].material[material3].materialdata[keyword]
    
UScumsumlandfill_glass = np.cumsum(USlandfill_glass)
UScumsumlandfill_silicon = np.cumsum(USlandfill_silicon)
UScumsumlandfill_silver = np.cumsum(USlandfill_silver)


plt.plot(r1.scenario[PCAs[0]].data['year'], UScumsumlandfill_glass, label='Glass')
plt.plot(r1.scenario[PCAs[0]].data['year'], UScumsumlandfill_silicon, label='Silicon')
plt.plot(r1.scenario[PCAs[0]].data['year'], UScumsumlandfill_silver, label='Silver')
'''


# In[ ]:





# In[ ]:





# In[ ]:





# # GEOPANDAS

# In[101]:


latitude_all =[]
longitude_all = []
cumulativewaste2050 = []
for scen in r1.scenario.keys():
    latitude_all.append(r1.scenario[scen].latitude)
    longitude_all.append(r1.scenario[scen].longitude)
    cumulativewaste2050.append(r1.scenario[scen].material['glass'].materialdata['mat_Total_Landfilled'].sum())


# In[102]:


import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon

street_map = gpd.read_file(r'C:\Users\sayala\Desktop\geopandas\cb_2018_us_nation_20m\cb_2018_us_nation_20m.shp')

# Show the map only
#fig, ax = plt.subplots(figsize=(10,15))
#street_map.plot(ax=ax)


# In[103]:


frame = { 'Latitude': latitude_all, 'Longitude': longitude_all, 'CumulativeWaste2050': cumulativewaste2050}   
df = pd.DataFrame(frame) 


# In[104]:


df.head()


# In[105]:


geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
geometry[:3]


# In[106]:


crs = {'init':'epsg:4326'}


# In[107]:


geo_df = gpd.GeoDataFrame(df, # specify our data
                         crs = crs, # specify our coordinate reference system
                         geometry = geometry) # specify the geometry list we created
geo_df.head()


# In[108]:


fig, ax = plt.subplots(figsize = (15,15))
street_map.plot(ax = ax, alpha = 0.4, color = "grey")
geo_df[geo_df['CumulativeWaste2050'] >= 1.918125e+09].plot(ax=ax, markersize = 20, color= "blue", marker = "o", label = "Bigger Than")
geo_df[geo_df['CumulativeWaste2050'] < 1.918125e+09].plot(ax=ax, markersize = 20, color= "red", marker = "o", label = "Less Than")
plt.xlim([-130, -60])
plt.ylim([20, 50])
plt.legend(prop={'size':15})


# In[ ]:


import random
import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon

latitude = random.sample(range(25, 45), 10) 
longitude = random.sample(range(-125, -65), 10) 
weight = random.sample(range(0, 500), 10) 

frame = { 'Latitude': latitude, 'Longitude': longitude, 'Weight': weight}   
df = pd.DataFrame(frame) 

geometry = [Point(xy) for xy in zip(df['Longitude'], df['Latitude'])]
crs = {'init':'epsg:4326'}
geo_df = gpd.GeoDataFrame(df, # specify our data
                         crs = crs, # specify our coordinate reference system
                         geometry = geometry) # specify the geometry list we created

fig, ax = plt.subplots(figsize = (15,15))
street_map.plot(ax = ax, alpha = 0.4, color = "grey")
geo_df[geo_df['Weight'] >=250].plot(ax=ax, markersize = 20, color= "blue", marker = "o", label = "Bigger Than")
geo_df[geo_df['Weight'] < 250].plot(ax=ax, markersize = 20, color= "red", marker = "o", label = "Less Than")
plt.xlim([-130, -60])
plt.ylim([20, 50])
plt.legend(prop={'size':15})


# In[ ]:


import geoplot


# In[ ]:


ax = street_map.kdeplot(
    geo_df, #clip=boroughs.geometry,
    shade=True, cmap='Reds',
    projection=geoplot.crs.AlbersEqualArea())
geoplot.polyplot(boroughs, ax=ax, zorder=1)


# In[ ]:





# In[ ]:


import scipy.stats
import seaborn.palettes
import seaborn.utils


# In[ ]:


axis = [-130, 48.1667, -70, 100.1667]


# In[ ]:


latlng_bounds = area.total_bounds
area = area.to_crs(epsg=3857)
axis = area.total_bounds

# Create the map stretching over the requested area
ax = area.plot(alpha=0)


# In[ ]:


# Calculate the KDE
data = np.c_[df.Longitude, df.Latitude]
kde = scipy.stats.gaussian_kde(data.T, bw_method="scott", weights=df.CumulativeWaste2050)
data_std = data.std(axis=0, ddof=1)
bw_x = getattr(kde, "scotts_factor")() * data_std[0]
bw_y = getattr(kde, "scotts_factor")() * data_std[1]
grid_x = grid_y = 100
x_support = seaborn.utils._kde_support(data[:, 0], bw_x, grid_x, 3, (axis[0], axis[2]))
y_support = seaborn.utils._kde_support(data[:, 1], bw_y, grid_y, 3, (axis[1], axis[3]))
xx, yy = np.meshgrid(x_support, y_support)
levels = kde([xx.ravel(), yy.ravel()]).reshape(xx.shape)


# In[ ]:


cset = ax.contourf(xx, yy, levels,
    20, # n_levels

    cmap=seaborn.palettes.blend_palette(('#ffffff10', '#ff0000af'), 6, as_cmap=True),
    antialiased=True,       # avoids lines on the contours to some extent
)


# In[ ]:





# In[ ]:


def add_basemap(ax, latlng_bounds, axis, url='https://a.basemaps.cartocdn.com/light_all/tileZ/tileX/tileY@2x.png'):
    prev_ax = ax.axis()
    # TODO: Zoom should surely take output pixel request size into account...
    zoom = ctx.tile._calculate_zoom(*latlng_bounds)
    while ctx.tile.howmany(*latlng_bounds, zoom, ll=True) > max_tiles:      # dont ever try to download loads of tiles
        zoom = zoom - 1
    print("downloading %d tiles with zoom level %d" % (ctx.tile.howmany(*latlng_bounds, zoom, ll=True), zoom))
    basemap, extent = ctx.bounds2img(*axis, zoom=zoom, url=url)
    ax.imshow(basemap, extent=extent, interpolation='bilinear')
    ax.axis(prev_ax)        # restore axis after changing the background
 
add_basemap(ax, latlng_bounds, axis)


# In[ ]:


import geopandas as gpd


import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

def make_plot(projection_name, projection_crs, extent, heat_data):
    """
    ?
    """
    fig = plt.figure()
    rect = 0.1, 0.1, 0.8, 0.8
    ax = fig.add_axes(rect, projection=projection_crs)

    # Set display limits to include a set region of latitude * longitude.
    # (Note: Cartopy-specific).
    ax.set_extent(extent, crs=projection_crs)

    # Add coastlines and meridians/parallels (Cartopy-specific).
    ax.coastlines(linewidth=0.2, color='black')
    ax.gridlines(crs=projection_crs, linestyle='-')

    lat = np.linspace(extent[0],extent[1],heat_data.shape[0])
    lon = np.linspace(extent[2],extent[3],heat_data.shape[1])
    Lat,Lon = np.meshgrid(lat,lon)
    ax.pcolormesh(Lat,Lon,np.transpose(heat_data))
    plt.savefig("Test_fig.pdf", bbox_inches='tight')


def main():
    #extent = (-65.0, -62, 44, 45.5)
    extent = (-90, -40, 30, 60)
    # Define some test points with latitude and longitude coordinates.
    #city_data = [('Halifax, NS', 44.67, -63.61, 'black'),
    #             ('Neighbour', 45, -63, 'blue'),
    #             ('Other_Place', 44.1, -64, 'red')]
    heat_data = np.random.normal(0.0,0.2,size=(100,150))

    # Demonstrate with two different display projections.
    # Define a Cartopy 'ordinary' lat-lon coordinate reference system.
    crs_latlon = ccrs.PlateCarree()
    make_plot('Equidistant Cylindrical', crs_latlon, extent, heat_data)
    #crs_ae = ccrs.LambertCylindrical()
    #make_plot('Lambert Cylindrical', crs_ae, extent, heat_data)

if __name__ == '__main__':
    main()
