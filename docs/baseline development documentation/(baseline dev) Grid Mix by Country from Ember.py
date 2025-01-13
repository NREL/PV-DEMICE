#!/usr/bin/env python
# coding: utf-8

# # Import and update Grid electricity mix by country Automatically
# This journal points at Ember grid electricity data, pulls the file, parses it for the countrywise grid mix percentages. These are then saved into the carbon baseline_countrygridmix.csv and used for the carbon calculations in PV ICE.

# In[1]:


import numpy as np
import pandas as pd
import os,sys
from pathlib import Path
import matplotlib.pyplot as plt
from urllib.request import urlretrieve
#import PV_ICE
cwd = os.getcwd() #grabs current working directory


# In[2]:


supportMatfolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines' / 'SupportingMaterial')
baselinesFolder = str(Path().resolve().parent.parent / 'PV_ICE' / 'baselines')
cwd


# In[3]:


#print("Working on a ", platform.system(), platform.release())
print("Python version ", sys.version)
print("Pandas version ", pd.__version__)
print("pyplot ", plt.matplotlib.__version__)
#print("PV_ICE version ", PV_ICE.__version__)


# In[6]:


url = 'https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/yearly_full_release_long_format.csv'


# In[7]:


storage_options = {'User-Agent': 'Mozilla/5.0'}
emberdata_raw = pd.read_csv(url, storage_options=storage_options)

emberdata_raw.head()


# In[8]:


#down select for only columsn of interest
emberdata = emberdata_raw.filter(items=['Area','Year','Variable','Unit','Value'])

#downselect for only variables of interest (that don't overlap/double count)
Variables = ['Bioenergy','Coal','Gas','Hydro','Nuclear','Other Fossil','Solar','Wind']
emberdata_vars = emberdata.loc[emberdata['Variable'].isin(Variables)]

#select only the % of energy generation, % only used for energy generation (I checked)
#emberdata_vars['Unit'].unique()
Units = ['%']
emberdata_vars_perc = emberdata_vars.loc[emberdata_vars['Unit'].isin(Units)]
emberdata_vars_perc.reset_index(drop=True, inplace=True)
emberdata_vars_perc


# In[9]:


emberdata_vars_perc['Area'].unique()


# In[10]:


#munge the Area strings into a more usable format (this takes a while!)
import re
def remove_substrings_regex(text, substrings):
    pattern = '|'.join(map(re.escape, substrings))
    return re.sub(pattern, '', text)

emberdata_vars_perc_rename = emberdata_vars_perc.copy()

#change specific country names to work with prior carbon name formating
emberdata_vars_perc_rename.loc[emberdata_vars_perc['Area']=="United Arab Emirates", "Area"] = "UAE"
emberdata_vars_perc_rename.loc[emberdata_vars_perc['Area']=="United States of America", "Area"] = "USA"
emberdata_vars_perc_rename.loc[emberdata_vars_perc['Area']=="Congo (the Democratic Republic of the)", "Area"] = "CongoDRC"
emberdata_vars_perc_rename.loc[emberdata_vars_perc['Area']=="Korea (the Democratic People's Republic of)", "Area"] = "North Korea"
emberdata_vars_perc_rename.loc[emberdata_vars_perc['Area']=="Lao People's Democratic Republic (the)", "Area"] = "Laos"

substrings = [" (the)", " (Islamic Republic of)", " (Bolivarian Republic of)", "n Federation", 
              ", State of", "n Arab Republic", ", the United Republic of", " Herzegovina"]
for row in range(0,len(emberdata_vars_perc_rename['Area'])):
    emberdata_vars_perc_rename.iloc[row,0] = remove_substrings_regex(emberdata_vars_perc_rename.iloc[row,0], substrings)

#emberdata_vars_perc['Area'].unique()


# In[11]:


emberdata_vars_perc_rename.loc[emberdata_vars_perc_rename['Area']=="Laos"]


# In[12]:


#emberdata_vars_perc.loc[emberdata_vars_perc['Area']=="Bahamas (the)"]
emberdata_vars_perc_rename['Area'].unique()


# In[13]:


#for unique values of renamed area, do a pivot table with year on index, variable on column, and value in thingy
gridmix_bycountry_2000topresent = pd.DataFrame()
Areas = emberdata_vars_perc_rename['Area'].unique() #an array
for a in range(0,len(Areas)):
    tempdf = emberdata_vars_perc_rename.loc[emberdata_vars_perc_rename['Area'] == Areas[a]] #select each area individually
    tempdf2 = tempdf.pivot(columns='Variable', values='Value', index='Year') #pivot table of this area
    tempdf_rename = tempdf2.add_prefix(str(Areas[a]+'_'))
    gridmix_bycountry_2000topresent = pd.concat([gridmix_bycountry_2000topresent,tempdf_rename], axis=1)

gridmix_bycountry_2000topresent


# In[19]:


#add in the 1995 to 2000 and present to 2050, ffill and bfill
indx_temp = pd.Series(range(2000,2051,1))
gridmix_bycountry_1995to2050 = gridmix_bycountry_2000topresent.reindex(indx_temp, method='nearest') #still leaving NaN if 2023 value NaN
gridmix_bycountry_1995to2050_full = gridmix_bycountry_1995to2050.fillna(method='ffill') #fix nan values throughout
gridmix_bycountry_1995to2050_full


# In[15]:


#emberdata_vars_perc_rename['Area'].unique()
areaofinterest = 'Bosnia'
gridmix_bycountry_1995to2050_full.filter(like=areaofinterest).plot(kind='area', legend='reverse').legend(bbox_to_anchor=(1, 0.5))


# In[21]:


gridmix_bycountry_1995to2050_full.to_csv(os.path.join(baselinesFolder,'CarbonLayer','baseline2050_countrygridmix.csv'))


# In[23]:


#add in the 1995 to 2000 and present to 2100, ffill and bfill
indx_temp = pd.Series(range(1995,2101,1))
gridmix_bycountry_1995to2100 = gridmix_bycountry_2000topresent.reindex(indx_temp, method='nearest') #still leaving NaN if 2023 value NaN
gridmix_bycountry_1995to2100_full = gridmix_bycountry_1995to2100.fillna(method='ffill') #fix nan values throughout
gridmix_bycountry_1995to2100_full


# In[24]:


gridmix_bycountry_1995to2100_full.to_csv(os.path.join(baselinesFolder,'CarbonLayer','baseline2100_countrygridmix.csv'))


# In[ ]:





# In[ ]:




