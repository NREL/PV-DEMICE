# -*- coding: utf-8 -*-
"""
Main.py contains the functions to calculate the different quantities of
materials in each step of the process. Reffer to the diagram on
Package-Overview for the steps considered.

Support functions include Weibull functions for reliability and failure; also,
functions to modify baseline values and evaluate sensitivity to the parameters.

"""

import numpy as np
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
import itertools
from pathlib import Path

global DATA_PATH # path to data files including module.json.  Global context
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'baselines'))


def read_baseline_material(scenario, material='None', file=None):

    if file is None:
        try:
            file = _interactive_load('Select baseline file')
        except:
            raise Exception('Interactive load failed. Tkinter not supported' +
                            'on this system. Try installing X-Quartz and ' +
                            'reloading')


def _interactive_load(title=None):
    # Tkinter file picker
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk()
    root.withdraw()  # Start interactive file input
    root.attributes("-topmost", True)  # Bring window into foreground
    return filedialog.askopenfilename(parent=root, title=title)


def _readPVICEFile(file):

    csvdata = open(str(file), 'r', encoding="UTF-8")
    csvdata = open(str(file), 'r', encoding="UTF-8-sig")
    firstline = csvdata.readline()
    secondline = csvdata.readline()

    head = firstline.rstrip('\n').split(",")
    meta = dict(zip(head, secondline.rstrip('\n').split(",")))

    data = pd.read_csv(csvdata, names=head)
    data.loc[:, data.columns != 'year'] = data.loc[:, data.columns !=
                                                   'year'].astype(float)

    return data, meta


def _unitReferences(keyword):
    '''
    Specify units for variable in scenario or materials

    Parameters
    ----------
    keyword : str
       String of scenario or material column label

    Returns
    -------
    yunits : str
        Unit specific to the keyword provided
    '''

    moduleDictionary = {
        'year': {'unit': 'Years', 'source': 'input'},
        'new_Installed_Capacity_[MW]': {'unit': 'Power [MW]',
                                        'source': 'input'},
        'mod_eff': {'unit': 'Efficiency $\eta$ [%]',
                    'source': 'input'},
        'mod_reliability_t50': {'unit': 'Years',
                                'source': 'input'},
        'mod_reliability_t90': {'unit': 'Years',
                                'source': 'input'},
        'mod_degradation': {'unit': 'Percentage [%]',
                            'source': 'input'},
        'mod_lifetime': {'unit': 'Years',
                         'source': 'input'},
        'mod_MFG_eff': {'unit': 'Efficiency $\eta$ [%]',
                        'source': 'input'},
        'mod_EOL_collection_eff': {'unit': 'Efficiency $\eta$ [%]',
                                   'source': ' input'},
        'mod_EOL_collected_recycled': {'unit': 'Percentage [%]',
                                       'source': 'input'},
        'mod_Repair': {'unit': 'Percentage [%]',
                       'source': 'input'},
        'mod_MerchantTail': {'unit': 'Percentage [%]',
                             'source': 'input'},
        'mod_Reuse': {'unit': 'Percentage [%]',
                      'source': 'input'},
        'Area': {'unit': 'm$^2$',
                 'source': 'generated'},
        'Cumulative_Area_EOLby_Failure': {'unit': 'm$^2$',
                                               'source': 'generated'},
        'Cumulative_Area_EOLby_ProjectLifetime': {'unit': 'm$^2$',
                                                       'source': 'generated'},
        'Cumulative_Area_atEOL': {'unit': 'm$^2$', 'source': 'generated'},
        'Cumulative_Active_Area': {'unit': 'm$^2$', 'source': 'generated'},
        'Effective_Capacity_[W]': {'unit': 'Power [W]', 'source': 'generated'},
        'EOL_on_Year_0': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_1': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_2': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_3': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_4': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_5': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_6': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_7': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_8': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_9': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_10': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_11': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_12': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_13': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_14': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_15': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_16': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_17': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_18': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_19': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_20': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_21': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_22': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_23': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_24': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_25': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_26': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_27': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_28': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_29': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_30': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_31': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_32': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_33': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_34': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_35': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_36': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_37': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_38': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_39': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_40': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_41': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_42': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_43': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_44': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_45': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_46': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_47': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_48': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_49': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_50': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_51': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_52': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_53': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_54': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_on_Year_55': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_Collected': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_NotCollected': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_Recycled': {'unit': 'm$^2$', 'source': 'generated'},
        'EOL_NotRecycled_Landfilled': {'unit': 'm$^2$', 'source': 'generated'}
                        }

    materialDictionary = {
        'year': {'unit': 'Years', 'source': 'input'},
        'mat_virgin_eff': {'unit': 'Efficiency $\eta$ [%]', 'source': 'input'},
        'mat_massperm2': {'unit': 'Mass [g]', 'source': 'input'},
        'mat_MFG_eff': {'unit': 'Efficiency $\eta$ [%]', 'source': 'input'},
        'mat_MFG_scrap_recycled': {'unit': 'Percentage [%]',
                                   'source': 'input'},
        'mat_MFG_scrap_Recycled': {'unit': 'Efficiency $\eta$ [%]',
                                   'source': 'input'},
        'mat_MFG_scrap_Recycled_into_HQ': {'unit': 'Percentage [%]',
                                           'source': 'input'},
        'mat_MFG_scrap_Recycled_into_HQ_Reused4MFG': {'unit': 'Percentage [%]',
                                                      'source': 'input'},
        'mod_EOL_p5_recycled': {'unit': 'Percentage [%]', 'source': 'input'},
        'mat_EOL_Recycling_yield': {'unit': 'Efficiency $\eta$ [%]',
                                    'source': 'input'},
        'mat_EOL_Recycled_into_HQ': {'unit': 'Percentage [%]',
                                     'source': 'input'},
        'mat_EOL_RecycledHQ_Reused4MFG': {'unit': 'Percentage [%]',
                                          'source': 'input'},
        'mat_modules_NotRecycled': {'unit': 'Mass [g]',
                                    'source': 'generated'},
        'mat_modules_NotCollected': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_EOL_sento_Recycling': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_EOL_NotRecycled_Landfilled': {'unit': 'Mass [g]',
                                           'source': 'generated'},
        'mat_EOL_Recycled': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_EOL_Recycled_Losses_Landfilled': {'unit': 'Mass [g]',
                                               'source': 'generated'},
        'mat_EOL_Recycled_2_HQ': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_EOL_Recycled_2_OQ': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_EOL_Recycled_HQ_into_MFG': {'unit': 'Mass [g]',
                                         'source': 'generated'},
        'mat_EOL_Recycled_HQ_into_OU': {'unit': 'Mass [g]',
                                        'source': 'generated'},
        'mat_UsedinManufacturing': {'unit': 'Mass [g]',
                                    'source': 'generated'},
        'mat_Manufacturing_Input': {'unit': 'Mass [g]',
                                    'source': 'generated'},
        'mat_MFG_Scrap': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_MFG_Scrap_Sentto_Recycling': {'unit': 'Mass [g]',
                                           'source': 'generated'},
        'mat_MFG_Scrap_Landfilled': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_MFG_Scrap_Recycled_Successfully': {'unit': 'Mass [g]',
                                                'source': 'generated'},
        'mat_MFG_Scrap_Recycled_Losses_Landfilled': {'unit': 'Mass [g]',
                                                     'source': 'generated'},
        'mat_MFG_Recycled_into_HQ': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_MFG_Recycled_into_OQ': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_MFG_Recycled_HQ_into_MFG': {'unit': 'Mass [g]',
                                         'source': 'generated'},
        'mat_MFG_Recycled_HQ_into_OU': {'unit': 'Mass [g]',
                                        'source': 'generated'},
        'mat_Virgin_Stock': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_Total_EOL_Landfilled': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_Total_MFG_Landfilled': {'unit': 'Mass [g]',
                                     'source': 'generated'},
        'mat_Total_Landfilled': {'unit': 'Mass [g]', 'source': 'generated'},
        'mat_Total_Recycled_OU': {'unit': 'Mass [g]', 'source': 'generated'},
        'Yearly_Sum_Area_EOLby_Failure': {'unit': 'Area [m$^2$]',
                                               'source': 'generated'}
        }

    if keyword in moduleDictionary.keys():
        yunits = moduleDictionary[keyword]['unit']
    elif keyword in materialDictionary.keys():
        yunits = materialDictionary[keyword]['unit']
    else:
        print("Warning: Keyword / Units not Found")
        yunits = 'UNITS'

    return yunits


def distance(s_lat, s_lng, e_lat, e_lng):
    """
    # Haversine formula for numpy arrays
    # Author: MalyutinS
    # imported from comment on: https://gist.github.com/rochacbruno/2883505
    # Example:
    # s_lat = 45; s_lng = -110; e_lat=[33, 44]; e_lng = [-115, -140]
    # Returns distance from the source point  to the two ending points:
    # r = distance(s_lat, s_lng, e_lat, e_lng)
    # r = array([1402.24996689, 2369.0150434 ])
    #
    """

    # approximate radius of earth in km
    R = 6373.0

#    s_lat = s_lat*np.pi/180.0
    s_lat = np.deg2rad(s_lat)
    s_lng = np.deg2rad(s_lng)
    e_lat = np.deg2rad(e_lat)
    e_lng = np.deg2rad(e_lng)

    d = (np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) *
         np.sin((e_lng - s_lng)/2)**2)
    distance = 2 * R * np.arcsin(np.sqrt(d))

    return distance


def drivingdistance(origin, destination, APIkey):
    """
    Creates call for google-maps api to get driving directions betwen 2 points.

    Input
    -----
    origin: array
        [lat, lon] expected
    destination: array
        [lat, lon] expected
    APYkey: str
        String
    """

    lat1, lon1 = origin
    lat2, lon2 = destination

    gm_url = ('https://maps.googleapis.com/maps/api/directions/xml?' +
              'origin='+str(lat1) + ',' + str(lon1) +
              '&destination=' + str(lat2) + ','+str(lon2) +
              '&key='+APIkey)

    return gm_url


class Simulation:
    """
    The ScenarioObj top level class is used to work on Circular Economy
    scenario objects, keep track of filenames, data for module and materials,
    operations modifying the baselines, etc.

    Parameters
    ----------
    name : text to append to output files
    nowstr : current date/time string
    path : working directory with circular economy results

    Methods
    -------
    __init__ : initialize the object
    _setPath : change the working directory

    """

    def __init__(self, name=None, path=None, baselinepath=None):
        '''
        initialize ScenarioObj with path of Scenario's baseline of module and
        materials as well as a basename to append to

        Parameters
        ----------
        name: string, append temporary and output files with this value
        path: location of Radiance materials and objects

        Returns
        -------
        none
        '''

        self.path = ""             # path of working directory
        self.name = ""         # basename to append

        now = datetime.datetime.now()
        self.nowstr = (str(now.date()) + '_' + str(now.hour) +
                       str(now.minute) + str(now.second))

        if path is None:
            self._setPath(os.getcwd())
        else:
            self._setPath(path)

        if name is None:
            self.name = self.nowstr  # set default filename for output files
        else:
            self.name = name

        if baselinepath is None:
            self.baselinepath = DATA_PATH
            print("Baseline folder directed to default: ", DATA_PATH)
        else:
            self.baselinepath = baselinepath

        self.scenario = {}

    def pickle_Sim(self, filename=None):
        import pickle
        if filename is None:
            filename = self.name + '.pkl'
            filename = os.path.join(self.path, filename)
        with open(filename, 'wb') as outp:  # Overwrites any existing file
            pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)

    def load_Simpickle(filename):
        import pickle
        return pickle.load(open(filename, "rb", -1))

    def _setPath(self, path):
        """
        setPath - move path and working directory

        """
        self.path = os.path.abspath(path)

        print('path = ' + path)
        try:
            os.chdir(self.path)
        except OSError as exc:
            LOGGER.error('Path doesn''t exist: %s' % (path))
            LOGGER.exception(exc)
            raise (exc)

        # check for path in the new Radiance directory:
        def _checkPath(path):  # create the file structure if it doesn't exist
            if not os.path.exists(path):
                os.makedirs(path)
                print('Making path: '+path)

        _checkPath('raw')
        _checkPath('input')
        _checkPath('output')
        _checkPath('figures')

    def createScenario(self, name, massmodulefile=None, energymodulefile=None,
                       file=None):

        import re
        
        if file is not None:
            print("Please use massmodulefile or energymodulefile as inputs " +
                  " to this function.")
            return
        
        if massmodulefile is None:
            files = [f for f in os.listdir(DATA_PATH) if re.match(
                r'baseline_modules_mass', f)]
            print("Please pass one of the following options: ", files)
            return
        elif os.path.isfile(massmodulefile) is False:
            if os.path.isfile(os.path.join(self.baselinepath, massmodulefile)):
                massmodulefile = os.path.join(self.baselinepath,
                                              massmodulefile)
            else:
                print('File not found, check path to folder if passed is ' +
                      'correct or that baseline folder is correct',
                      massmodulefile)
                return

        if energymodulefile is None:
            files = [f for f in os.listdir(DATA_PATH) if re.match(
                r'baseline_modules_energy', f)]
            print("No energy module file passed. If desired, pass one of the" +
                  " following options: ", files)
        elif os.path.isfile(energymodulefile) is False:
            if os.path.isfile(os.path.join(self.baselinepath,
                                           energymodulefile)):
                energymodulefile = os.path.join(self.baselinepath,
                                                energymodulefile)
            else:
                print('File not found, check path to folder if passed is ' +
                      'correct or that baseline folder is correct',
                      energymodulefile)
                return

        self.scenario[name] = Scenario(name, file=file,
                                       massmodulefile=massmodulefile,
                                       energymodulefile=energymodulefile)

    def modifyScenario(self, scenarios, stage, value, start_year=None):

        if start_year is None:
            start_year = int(datetime.datetime.now().year)

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        selectyears = self.scenario[scenarios[0]].dataIn_m['year'] >= start_year

        if isinstance(value, (pd.Series)):
            for scen in scenarios:
                timeshift = start_year - self.scenario[scen].dataIn_m.iloc[0,0]
                self.scenario[scen].dataIn_m.loc[timeshift:, stage] = value.values

        else:
            for scen in scenarios:
                self.scenario[scen].dataIn_m.loc[selectyears, stage] = value
                
                
    def saveSimulation(self, scenarios=None, materials=None, customname=None,
                       overwrite=True):
        
        if customname is None:
            customname = ''

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]
    
        if materials is None:
            materials = list(self.scenario[scenarios[0]].material.keys())
        else:
            if isinstance(materials, str):
                materials = [materials]

        def _existsandSavequestionmark(attribute, savefolder, customname, overwrite, scen, mat=None, metattribute=None):
            if mat is None:
                titlecsv = scen + '_' + attribute + customname + '.csv'
                pviceobj = self.scenario[scen]
            else:
                titlecsv = scen + '_' + mat + '_' + attribute + customname + '.csv'
                pviceobj = self.scenario[scen].material[mat]
            
            filefullpath = os.path.join(savefolder, titlecsv)
            if (os.path.isfile(filefullpath)) and (overwrite is False):
                print(filefullpath + " exists and set to not overwrite, skipping.")
            else:
                if hasattr(pviceobj, attribute):
                    dffoo = getattr(pviceobj, attribute)
                    if metattribute is not None:
                        if hasattr(pviceobj, metattribute):
                            mydict = getattr(pviceobj, metattribute)
                            metdata = pd.DataFrame(mydict, index=[0])
                            dffoo = pd.concat([metdata, dffoo], axis=0)
                    dffoo.to_csv(os.path.join(savefolder, titlecsv))
#                    dffoo.to_csv(os.path.join(savefolder, titlecsv), index_col=False)

        for scen in scenarios:

            _existsandSavequestionmark('dataIn_m', 'input', customname, overwrite, scen, mat=None, metattribute='metdataIn_m')
            _existsandSavequestionmark('dataIn_e', 'input', customname, overwrite, scen, mat=None, metattribute='metdataIn_e')
            _existsandSavequestionmark('dataOut_m', 'output', customname, overwrite, scen)
            _existsandSavequestionmark('dataOut_e', 'output', customname, overwrite, scen)
            _existsandSavequestionmark('dataDebug_m', 'output', customname, overwrite, scen)
                        
            for mat in materials:
                _existsandSavequestionmark('matdataIn_m', 'input', customname, overwrite, scen, mat, metattribute='matmetdataIn_m')
                _existsandSavequestionmark('matdataIn_e', 'input', customname, overwrite, scen, mat, metattribute='matmetdataIn_e')
                _existsandSavequestionmark('matdataOut_m', 'output', customname, overwrite, scen, mat)
                _existsandSavequestionmark('matdataOut_e', 'output', customname, overwrite, scen, mat)
        
        print(":) Saved Input and Output Dataframes")

    def modifyScenarioEnergy(self, scenarios, stage, value, start_year=None):

        if start_year is None:
            start_year = int(datetime.datetime.now().year)

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        selectyears = self.scenario[scenarios[0]].dataIn_e['year'] >= start_year

        if isinstance(value, (pd.Series)):
            for scen in scenarios:
                timeshift = start_year - self.scenario[scen].dataIn_e.iloc[0,0]
                self.scenario[scen].dataIn_e.loc[timeshift:, stage] = value.values

        else:
            for scen in scenarios:
                self.scenario[scen].dataIn_e.loc[selectyears, stage] = value


    def calculateFlows(self, scenarios=None, materials_input=None,
                       weibullInputParams=None, bifacialityfactors=None,
                       reducecapacity=True, debugflag=False,
                       installByArea=None, nameplatedeglimit=None):
        
        # #create a check that the start year on mass and energy files are the same
        # for scen in scenarios:
        #     mod_m_startyear = self.scenario[scen].dataIn_m.iloc[0,0]
        #     mod_e_startyear = self.scenario[scen].dataIn_e.iloc[0,0]
            
        #     if  mod_m_startyear != mod_e_startyear:
        #         print('The start year of mass and energy files do not match, please fix! Mass: '+str(mod_m_startyear)+' Energy: '+str(mod_e_startyear))
        #         return
        #     for mat in materials:
        #         if self.scenario[scen].material[mat].matdataIn_m.iloc[0,0] != self.scenario[scen].material[mat].matdataIn_e.iloc[0,0]:
        #             print('The start year of '+str(mat)+' mass and energy files do not match, please fix!')
        #             return
        #         if self.scenario[scen].material[mat].matdataIn_m.iloc[0,0] != mod_m_startyear:
        #             print('Start year of '+str(mat)+' mass file does not match module start year, please fix!')
        #             return
        
        
        self.calculateMassFlow(scenarios=scenarios, materials_input=None,
                               weibullInputParams=weibullInputParams,
                               bifacialityfactors=bifacialityfactors,
                               reducecapacity=reducecapacity,
                               debugflag=debugflag,
                               installByArea=installByArea,
                               nameplatedeglimit=nameplatedeglimit)

        self.calculateEnergyFlow(scenarios=scenarios, materials_input=None)
        
        #self.calculateCarbonFlows(scenarios=scenarios,materials_input=materials)

    def calculateMassFlow(self, scenarios=None, materials_input=None,
                          weibullInputParams=None, bifacialityfactors=None,
                          reducecapacity=False, debugflag=False,
                          installByArea=None, nameplatedeglimit=None,
                          secondlifenameplatedeglimit = None):
        '''
        Function takes as input a baseline dataframe already imported,
        with the right number of columns and content.
        It returns the dataframe with all the added calculation columns.

        Parameters
        ------------
        weibullInputParams : None
            Dictionary with 'alpha' and 'beta' value for shaping the weibull
            curve. beta is sometimes exchanged with lifetime, for example on
            Irena 2016 values beta = 30. If weibullInputParams = None,
            alfa and beta are calcualted from the t50 and t90 columns on the
            module baseline.
        scenarios : None
            string with the scenario name or list of strings with
            scenarios names to loop over. Must exist on the PV ICE object.
        materials : None
            string with the material name or list of strings with the
            materials names to loop over. Must exists on the PV ICE object
            scenario(s) modeled.
        bifacialityfactors : str
            File with bifacialtiy factors for each year under consideration
        installByArea : list floats
            When deploying each generation, it overrides using
            `new_Installed_Capacity_[MW]` to calculate deployed area, and
            installs this area instead calculating the installed capacity based
            on the module characteristics (efficiency and bifaciality factor).
            Length must match the years in the loaded dataframes.
        nameplatedeglimit : float
            Limit at which if the nameplate power is below they will be
            trashed. i.e. 0.8 default.
        secondlifenameplatedeglimit : float
            Limit at which if the nameplate power is below at their second life,
            the modules will be trashed. i.e. 0.5 default. 

        Returns
        --------
        df: dataframe
            input dataframe with addeds columns for the calculations of
            recycled, collected, waste, installed area, etc.

        '''

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        if nameplatedeglimit is None:
            nameplatedeglimit = 0.8

        if secondlifenameplatedeglimit is None:
            secondlifenameplatedeglimit = 0.5

        print(">>>> Calculating Material Flows <<<<\n")

        for scen in scenarios:

            print("Working on Scenario: ", scen)
            print("********************")
            df = self.scenario[scen].dataIn_m.copy()
            initialCols = df.keys()

            # Constant
            if bifacialityfactors is not None:
                bf = pd.read_csv(bifacialityfactors)
                df['irradiance_stc'] = 1000.0 + bf['bifi']*100.0
                # W/m^2 (min. Bifacial STC Increase)
            else:
                df['irradiance_stc'] = 1000.0  # W/m^2

            # Renaming and re-scaling
            df['t50'] = df['mod_reliability_t50']
            df['t90'] = df['mod_reliability_t90']

            # Calculating Area and Mass

            # Method to pass mass instead of calculating by Power to Area
            if 'Mass_[MetricTonnes]' in df:
                df['new_Installed_Capacity_[W]'] = 0
                df['new_Installed_Capacity_[MW]'] = 0
                df['Area'] = df['Mass_[MetricTonnes]']
                print("Warning, this is for special debuging of Wambach " +
                      "procedure. Make sure to use `Wambach Module`")
            # Method to pass Area to then calculate Power
            elif installByArea is not None:
                df['Area'] = installByArea
                df['new_Installed_Capacity_[W]'] = ((df['mod_eff']*0.01) *
                                                    df['irradiance_stc'] *
                                                    df['Area'])  # W
                df['new_Installed_Capacity_[MW]'] = (
                    df['new_Installed_Capacity_[W]']/1000000)
                print("Calculating installed capacity based on installed Area")

            # Standard method to calculate Area from the Power
            else:
                #negative deployment check, error, correct
                if (df['new_Installed_Capacity_[MW]'].values<0).any():
                    print('You have at least 1 negative annual deployment! All years of negative deployment have been set to 0.')
                    df.loc[df['new_Installed_Capacity_[MW]']<0,'new_Installed_Capacity_[MW]'] = 0.0
                
                df['new_Installed_Capacity_[W]'] = (
                    df['new_Installed_Capacity_[MW]']*1e6)

                if reducecapacity:
                    df['Area'] = (df['new_Installed_Capacity_[W]'] /
                                  (df['mod_eff']*0.01)/df['irradiance_stc'])
                    # m^2
                else:
                    df['Area'] = (df['new_Installed_Capacity_[W]'] /
                                  (df['mod_eff']*0.01)/1000.0)  # m^2

            df['Area'] = df['Area'].fillna(0)  # Chagne na's to 0s.

            # Calculating Wast by Generation by Year, and Cum. Waste by Year.
            Generation_EOL_pathsG = []
            Matrix_Landfilled_noncollected = []
            Matrix_areaEOL_degradation_all = []
            Matrix_Failures = []
            weibullParamList = []


            df['Yearly_Sum_Area_EOLby_Failure'] = 0
            df['Yearly_Sum_Power_EOLby_Failure'] = 0
            df['Yearly_Sum_Area_EOLby_Degradation'] = 0
            df['Yearly_Sum_Power_EOLby_Degradation'] = 0
            df['Yearly_Sum_Area_EOLby_ProjectLifetime'] = 0
            df['Yearly_Sum_Power_EOLby_ProjectLifetime'] = 0

            df['Yearly_Sum_Area_atEOL'] = 0  # Failure + Degradation + ProjcLife
            df['Yearly_Sum_Power_atEOL'] = 0
            df['Yearly_Sum_Area_PathsBad'] = 0 # should be degradation, failures not fixed
            df['Yearly_Sum_Power_PathsBad'] = 0
            df['Yearly_Sum_Area_PathsGood'] = 0  # should be proj lifetimes
            df['Yearly_Sum_Power_PathsGood'] = 0

            df['Landfill_0_ProjLife'] = 0 # non collected

            df['Repaired_Area'] = 0
            df['Repaired_[W]'] = 0

            df['Resold_Area'] = 0
            df['Resold_[W]'] = 0

            df['MerchantTail_Area'] = 0
            df['MerchantTail_[W]'] = 0

            df['Cumulative_Active_Area'] = 0 # Effective installed area
            df['Effective_Capacity_[W]'] = 0 # Effective installed capacity 
            # i.e  installed - degrad - fails - eol PL ..

            df['Power_Degraded_[W]'] = 0   # The way it is calculated it is 
                                           # 'cumulative' or relative from the nameplate
                                           # to each year. 
            
            for generation, row in df.iterrows():
                # generation is an int 0,1,2,.... etc.
                # generation=4
                # row=df.iloc[generation]

                if weibullInputParams:
                    weibullIParams = weibullInputParams
                elif 'weibull_alpha' in row:
                    # "Weibull Input Params passed internally as a column"
                    weibullIParams = {'alpha': row['weibull_alpha'],
                                      'beta': row['weibull_beta']}
                else:
                    # "Calculating Weibull Params from Modules t50 and T90"
                    t50, t90 = row['t50'], row['t90']
                    weibullIParams = weibull_params({t50: 0.50, t90: 0.90})

                f = weibull_cdf(weibullIParams['alpha'],
                                weibullIParams['beta'])

                weibullParamList.append(weibullIParams)

                x = np.clip(df.index - generation, 0, np.inf)
                cdf = list(map(f, x))
                # TODO: Check this line, does it need commas or remove space
                # for linting?
                pdf = [0] + [j - i for i, j in zip(cdf[:-1], cdf[1:])]

                activearea = row['Area']
                if np.isnan(activearea):
                    activearea = 0

                activeareacount = []
                activepowercount = []  # Active area production.

                areaEOL_failure_notrepaired_all = []
                powerEOL_failure_notrepaired_all = []

                areaEOL_ProjLife_all = []
                powerEOL_ProjLife_all = []

                area_repaired_all = []
                power_repaired_all = []

                area_resold_all = []
                power_resold_all = []
                
                area_merchantTail_all = []
                power_merchantTail_all = []
                
                areaEOL_degradation_all = []
                powerEOL_degradation_all = []
                
                areaEOL_ProjLife_collected_PG_3to5_all = []
                powerEOL_ProjLife_collected_PG_3to5_all = []

                areaEOL_ProjLife_notcollected_L0_all = []
                powerEOL_ProjLife_notcollected_L0_all = []

                power_degraded_all = []
                # Age 0, nothing dies <3

                active = 0
                secondlife = False

                for age in range(len(cdf)):
                    
                    if x[age] == 0.0:
                        activeareacount.append(0)
                        activepowercount.append(0)

                        areaEOL_failure_notrepaired_all.append(0)
                        powerEOL_failure_notrepaired_all.append(0)
                        areaEOL_ProjLife_all.append(0)
                        powerEOL_ProjLife_all.append(0)
                        area_resold_all.append(0)
                        power_resold_all.append(0)
                        area_merchantTail_all.append(0)
                        power_merchantTail_all.append(0)
                        areaEOL_degradation_all.append(0)
                        powerEOL_degradation_all.append(0)
                        area_repaired_all.append(0)
                        power_repaired_all.append(0)
                        areaEOL_ProjLife_collected_PG_3to5_all.append(0)
                        powerEOL_ProjLife_collected_PG_3to5_all.append(0)             
                        areaEOL_ProjLife_notcollected_L0_all.append(0)
                        powerEOL_ProjLife_notcollected_L0_all.append(0)
                        power_degraded_all.append(0)
                        
                    else:
                        active += 1
                        removed_projectlifetime = 0
                        landfilled_noncollected = 0
                        
                        deg_nameplate = (1-row['mod_degradation']*0.01)**active
                        poweragegen = (row['mod_eff'] * 0.01 *
                                       row['irradiance_stc']*deg_nameplate)
                        powerinitgen = row['mod_eff'] * 0.01 * row['irradiance_stc']
                        
                        
                        # 1. Check if remaining cohort has degraded
    
                        power_degradaded = activearea * (powerinitgen - poweragegen) 
    
                        if secondlife:
                            nameplatedeglimiteval = secondlifenameplatedeglimit
                        else:
                            nameplatedeglimiteval = nameplatedeglimit
    
                        if deg_nameplate < nameplatedeglimiteval:
                            # TODO check this! killing and not sending
                            # to EOL collection paths,
                            areaEOL_degradation = activearea
                            powerEOL_degradation = (
                                areaEOL_degradation * poweragegen)
                            
                            # Reduntant as it is performed in the MATRIX later on PBD
                            '''
                            areaEOL_degradation_collected = (
                                areaEOL_degradation *
                                (df.iloc[age]['mod_EOL_collection_eff'] *
                                 0.01))
                            powerEOL_degradation_collected = areaEOL_degradation_collected * poweragegen
                            areaEOL_Deg_notcollected_L0 = areaEOL_degradation - areaEOL_degradation_collected
                            powerEOL_Deg_notcollected_L0 = areaEOL_Deg_notcollected_L0*poweragegen
                            '''
                            activearea = 0
                        else:
                            areaEOL_degradation = 0
                            powerEOL_degradation = 0
                            
                            #areaEOL_degradation_collected = 0
                            #powerEOL_degradation_collected = 0
                            #areaEOL_Deg_notcollected_L0 = 0
                            #powerEOL_Deg_notcollected_L0 = 0
    
                        # 3. EoL Project Lifetime 
                        if age != int(row['mod_lifetime']+generation):
                            #removed_projectlifetime = 0
                            #landfilled_noncollected = 0
                            area_merchantTail = 0
                            power_merchantTail = 0
                            area_resold = 0
                            power_resold = 0
                            areaEOL_ProjLife_notcollected_L0 = 0
                            powerEOL_ProjLife_notcollected_L0 = 0
                            areaEOL_ProjLife_collected_PG_3to5 = 0
                            powerEOL_ProjLife_collected_PG_3to5 = 0
                            areaEOL_ProjLife = 0
                            powerEOL_ProjLife = 0
                        else:
                            # activearea_temp = activearea
                            area_merchantTail = (
                                    activearea *
                                    (df.iloc[age]['mod_MerchantTail']*0.01))
                            power_merchantTail = area_merchantTail*poweragegen
    
                            if area_merchantTail > 0:
                                secondlife = True
                                
                            # internal - removed_projectlifetime
                            area_removed_projectlifetime = (activearea -
                                                        area_merchantTail)
    
                            # internal - area_removed_collected (pre-resold)
                            area_ProjLife_collected = (
                                area_removed_projectlifetime *
                                (df.iloc[age]['mod_EOL_collection_eff'] *
                                 0.01))
                            areaEOL_ProjLife_notcollected_L0 = (
                                area_removed_projectlifetime-area_ProjLife_collected)
    
                            powerEOL_ProjLife_notcollected_L0 = areaEOL_ProjLife_notcollected_L0 * poweragegen
                            area_resold = (
                                area_ProjLife_collected *
                                (df.iloc[age]['mod_EOL_pg0_resell']*0.01))
                            power_resold = area_resold*poweragegen
    
                            areaEOL_ProjLife_collected_PG_3to5 = (
                                area_ProjLife_collected - area_resold)
    
                            powerEOL_ProjLife_collected_PG_3to5 = (
                                areaEOL_ProjLife_collected_PG_3to5 * poweragegen)
    
                            activearea = area_merchantTail + area_resold
    
                            # removed_projectlifetime does not include
                            # Merchant Tail & Resold as they went back to
                            # active
                            areaEOL_ProjLife = (areaEOL_ProjLife_collected_PG_3to5 +
                                               areaEOL_ProjLife_notcollected_L0)
                                    # Same as removed_ProjLife - area_Resold
                            powerEOL_ProjLife = (
                                areaEOL_ProjLife*poweragegen)
    
                        # 2. Calculate failures
                        activeareaprev = activearea
                        failures = row['Area']*pdf[age]
    
                        if failures > activearea:
                            failures = activearea
    
    
                        area_repaired = (failures *
                                          df.iloc[age]['mod_Repair']*0.01)
                        power_repaired = area_repaired*poweragegen
    
                        areaEOL_Failures_notrepaired = failures-area_repaired
                        powerEOL_Failures_notrepaired = areaEOL_Failures_notrepaired*poweragegen
    
                        activearea = activeareaprev-areaEOL_Failures_notrepaired
    
    
                        # Start appending the yearly age values
    
                        power_degraded_all.append(power_degradaded)
                        
                        areaEOL_degradation_all.append(areaEOL_degradation)
                        powerEOL_degradation_all.append(powerEOL_degradation)
    
                        area_repaired_all.append(area_repaired)
                        power_repaired_all.append(power_repaired)
                        
                        areaEOL_failure_notrepaired_all.append(areaEOL_Failures_notrepaired)
                        powerEOL_failure_notrepaired_all.append(powerEOL_Failures_notrepaired)
    
                        area_merchantTail_all.append(area_merchantTail)
                        power_merchantTail_all.append(power_merchantTail)
    
                        area_resold_all.append(area_resold)
                        power_resold_all.append(power_resold)
                        
                        # has collected and non collected
                        # but not merchant tailed and resold
                        areaEOL_ProjLife_all.append(areaEOL_ProjLife)
                        powerEOL_ProjLife_all.append(powerEOL_ProjLife)
    
                        # noncollected from project lifetime ((only one that had to be
                        # collected internally for calculating the resold. 
                        # Failures and degradation collection get calculated
                        # later on the matrixes directly))
                        areaEOL_ProjLife_notcollected_L0_all.append(areaEOL_ProjLife_notcollected_L0)
                        powerEOL_ProjLife_notcollected_L0_all.append(powerEOL_ProjLife_notcollected_L0)
                        
                        # Collected for Path Goods
                        areaEOL_ProjLife_collected_PG_3to5_all.append(areaEOL_ProjLife_collected_PG_3to5)
                        powerEOL_ProjLife_collected_PG_3to5_all.append(powerEOL_ProjLife_collected_PG_3to5)
    
                        activeareacount.append(activearea)
                        activepowercount.append(activearea*poweragegen)
    
                        # Generation age loop ends
    
                
                # !! Unelegantly Correcting Initial Years 
                try:
                    # becuase the clip starts with 0 for the installation year,
                    # dentifying installation year and adding initial area
                    fixinitialareacount = next((i for i, e in enumerate(x)
                                                if e), None) - 1
                    activeareacount[fixinitialareacount] = (
                        activeareacount[fixinitialareacount]+row['Area'])
                    activepowercount[fixinitialareacount] = (
                        activepowercount[fixinitialareacount] +
                        row['Area'] * row['mod_eff'] * 0.01 *
                        row['irradiance_stc'])
                    # TODO: note mentioned 'this addition seems to do nothing.'
                    # Check who /when wrote this and if theres need to fix.

                except:
                    # Last value doesnt have a xclip value of nonzero so it
                    # gives except. But it also means the loop finished for
                    # the calculations of Lifetime.
                    fixinitialareacount = len(cdf)-1
                    activeareacount[fixinitialareacount] = (
                        activeareacount[fixinitialareacount]+row['Area'])
                    activepowercount[fixinitialareacount] = (
                        activepowercount[fixinitialareacount] + row['Area'] *
                        row['mod_eff'] * 0.01 * row['irradiance_stc'])
                    print("Finished Area+Power Generation Calculations")

                #   area_disposed_of_generation_by_year = [element*row['Area']
                #                                           for element in pdf]
                # This used to be labeled as cumulative; but in the sense that
                # they cumulate yearly deaths for all cohorts that die.

                df['Yearly_Sum_Area_EOLby_Degradation'] += (
                    areaEOL_degradation_all)
                df['Yearly_Sum_Power_EOLby_Degradation'] += (
                    powerEOL_degradation_all)
                
                df['Power_Degraded_[W]'] += power_degraded_all
                
                df['Yearly_Sum_Area_EOLby_Failure'] += (
                    areaEOL_failure_notrepaired_all)
                df['Yearly_Sum_Power_EOLby_Failure'] += (
                    powerEOL_failure_notrepaired_all)

                df['Yearly_Sum_Area_EOLby_ProjectLifetime'] += (
                    areaEOL_ProjLife_all)
                df['Yearly_Sum_Power_EOLby_ProjectLifetime'] += (
                    powerEOL_ProjLife_all)

                df['Yearly_Sum_Area_atEOL'] += areaEOL_failure_notrepaired_all
                df['Yearly_Sum_Area_atEOL'] += areaEOL_ProjLife_all
                df['Yearly_Sum_Area_atEOL'] += areaEOL_degradation_all

                df['Yearly_Sum_Power_atEOL'] += powerEOL_failure_notrepaired_all
                df['Yearly_Sum_Power_atEOL'] += (powerEOL_ProjLife_all)
                df['Yearly_Sum_Power_atEOL'] += (powerEOL_degradation_all)

                df['Repaired_Area'] += area_repaired_all
                df['Repaired_[W]'] += power_repaired_all
                df['Resold_Area'] += area_resold_all
                df['Resold_[W]'] += power_resold_all
                df['MerchantTail_Area'] += area_merchantTail_all
                df['MerchantTail_[W]'] += power_merchantTail_all

                df['Yearly_Sum_Area_PathsBad'] += areaEOL_degradation_all
                df['Yearly_Sum_Power_PathsBad'] += powerEOL_degradation_all
                
                df['Yearly_Sum_Area_PathsBad'] += areaEOL_failure_notrepaired_all
                df['Yearly_Sum_Power_PathsBad'] += powerEOL_failure_notrepaired_all

                df['Yearly_Sum_Area_PathsGood'] += areaEOL_ProjLife_collected_PG_3to5_all
                df['Yearly_Sum_Power_PathsGood'] += powerEOL_ProjLife_collected_PG_3to5_all

                df['Cumulative_Active_Area'] += activeareacount
                df['Effective_Capacity_[W]'] += activepowercount

                df['Landfill_0_ProjLife'] += areaEOL_ProjLife_notcollected_L0_all


                # MATRIXES:
                Generation_EOL_pathsG.append(areaEOL_ProjLife_collected_PG_3to5_all)
                Matrix_Landfilled_noncollected.append(
                    areaEOL_ProjLife_notcollected_L0_all)
                Matrix_areaEOL_degradation_all.append(areaEOL_degradation_all)
                Matrix_Failures.append(areaEOL_failure_notrepaired_all)


            df['WeibullParams'] = weibullParamList

            # Cleanup of old calculations. Needed when you run twice function.
            try:
                df = df[df.columns.drop(list(df.filter(regex='^EOL_')))]
            except:
                print("Warning: Issue dropping EOL columns generated by "
                      "calculateMFC routine to overwrite")

            PG = pd.DataFrame(Generation_EOL_pathsG, columns=df.index,
                              index=df.index)

            L0 = pd.DataFrame(Matrix_Landfilled_noncollected,
                              columns=df.index, index=df.index)

            PBD = pd.DataFrame(Matrix_areaEOL_degradation_all, columns=df.index,
                              index=df.index)

            PBF = pd.DataFrame(Matrix_Failures, columns=df.index,
                              index=df.index)

            # Path Bad includes Path Bad from Project Lifetime and adding now
            #  the path bads from Failures atEOL (not repaired)
            PB = PBD + PBF

            # Updating Path Bad for collection efficiency.
            PBC = PB.mul(df['mod_EOL_collection_eff'].values*0.01)
            PBNC = PB - PBC

            # What doesn't get collected of Path Bad, goes to Landfill 0.
            L0 = L0 + PBNC

            # What goes on forward to Path Bads EoL Pathways is PBC.
            df = df.join(PG.add_prefix("EOL_PG_Year_"))
            df = df.join(L0.add_prefix("EOL_L0_Year_"))
            df = df.join(PBC.add_prefix("EOL_BS_Year"))

            df['EOL_Landfill0'] = L0.sum(axis=0)
            df['EOL_BadStatus'] = PBC.sum(axis=0)
            df['EOL_PG'] = PG.sum(axis=0)
            df['EOL_PATHS'] = (PBC+PG).sum(axis=0)

            # # Start to do EOL Processes PATHS GOOD
            #######################################

            # This Multiplication goes through Module and then material.
            # It is for processes that depend on each year as they improve,
            # i.e. Collection Efficiency,
            #
            # [  G1_1   G1_2    G1_3   G2_4 ...]       [N1
            # [    0    G2_1    G2_2   G2_3 ...]   X    N2
            # [    0      0     G3_1   G3_2 ...]        N3
            #                                           N4]
            #
            #      EQUAL
            # EOL_Collected =
            # [  G1_1*N1   G1_2 *N2   G1_3 *N3   G2_4 *N4 ...]
            # [    0       G2_1 *N2   G2_2 *N3   G2_3 *N4 ...]
            # [    0        0         G3_1 *N3   G3_2 *N4 ...]
            #

            # Re-scaling Path Good Matrix, becuase Resold modules already got
            # resold in the cohort loop above.
            # 'originalMatrix' = reducedMatrix x 100 / (100-p2)
            PG = PG.mul(100/(100-df['mod_EOL_pg0_resell']), axis=0)

            # Paths GOOD Check for 100% sum.
            # If P1-P5 over 100% will reduce landfill.
            # If P2-P5 over 100% it will shut down with Warning and Exit.
            #TODO: add check for less than 100%, adjust landfill
            SUMS1 = (df['mod_EOL_pg1_landfill'] + df['mod_EOL_pg0_resell'] +
                     df['mod_EOL_pg2_stored'] + df['mod_EOL_pg3_reMFG'] +
                     df['mod_EOL_pg4_recycled'])
            SUMS2 = (df['mod_EOL_pg0_resell'] +
                     df['mod_EOL_pg2_stored'] + df['mod_EOL_pg3_reMFG'] +
                     df['mod_EOL_pg4_recycled'])

            if (SUMS2 > 100).any():
                print("WARNING: Paths 0 through 4 should add to a 100%." +
                      " and there is no way to correct by updating " +
                      " path1_landfill. " +
                      " STOPPING SIMULATION NOW GO AND FIX YOUR INPUT. Tx <3")
                return

            if (SUMS1 > 100).any():
                print("Warning: Paths 0 through 4 add to above 100%;" +
                      "Fixing by Updating Landfill value to the remainder of" +
                      "100-(P0+P2+P3+P4).")
                df['mod_EOL_pg1_landfill'] = 100-SUMS2

            # PATH1
            PG1_landfill = PG.mul(df['mod_EOL_pg1_landfill'].values*0.01)
            df['PG1_landfill'] = list(PG1_landfill.sum())

            # PATH2
            PG2_stored = PG.mul(df['mod_EOL_pg2_stored'].values*0.01)
            df['PG2_stored'] = list(PG2_stored.sum())
            # TODO: Future development of Stored path here.

            # PATH3

            # TODO: evaluate if PG3_reMFG, PG3_reMFG_yield and
            # PG3_reMFG_unyield are given as output and if not are needed.
            # Also for BAD PATHS PB3_reMFG, PB3_reMFG_yield, PB3_reMFG_unyield

            PG3_reMFG = PG.mul(df['mod_EOL_pg3_reMFG'].values*0.01)
            df['PG3_reMFG'] = list(PG3_reMFG.sum())

            PG3_reMFG_yield = PG3_reMFG.mul(
                                        df['mod_EOL_reMFG_yield'].values*0.01)
            df['PG3_reMFG_yield'] = list(PG3_reMFG_yield.sum())

            PG3_reMFG_unyield = PG3_reMFG-PG3_reMFG_yield
            df['PG3_reMFG_unyield'] = list(PG3_reMFG_unyield.sum())

            # PATH 4
            PG4_recycled = PG.mul(df['mod_EOL_pg4_recycled'].values*0.01)
            df['PG4_recycled'] = list(PG4_recycled.sum())

            # PATH BADS:
            # ~~~~~~~~~~~

            # Check for 100% sum.
            # If P1-P5 over 100% will reduce landfill.
            # If P2-P5 over 100% it will shut down with Warning and Exit.
            SUMS1 = (df['mod_EOL_pb1_landfill'] +
                     df['mod_EOL_pb2_stored'] + df['mod_EOL_pb3_reMFG'] +
                     df['mod_EOL_pb4_recycled'])
            SUMS2 = (df['mod_EOL_pb2_stored'] + df['mod_EOL_pb3_reMFG'] +
                     df['mod_EOL_pb4_recycled'])

            if (SUMS2 > 100).any():
                print("WARNING: Paths B 1 through 4 should add to a 100%." +
                      " and there is no way to correct by updating " +
                      " path1_landfill. " +
                      " STOPPING SIMULATION NOW GO AND FIX YOUR INPUT. Tx <3")
                return

            if (SUMS1 > 100).any():
                print("Warning: Paths B 1 through 4 add to above 100%;" +
                      "Fixing by Updating Landfill value to the remainder of" +
                      "100-(P2+P3+P4).")
                df['mod_EOL_pb1_landfill'] = 100-SUMS2

            # PATH1
            PB1_landfill = PBC.mul(df['mod_EOL_pb1_landfill'].values*0.01)
            df['PB1_landfill'] = list(PB1_landfill.sum())

            # PATH2
            PB2_stored = PBC.mul(df['mod_EOL_pg2_stored'].values*0.01)
            df['PB2_stored'] = list(PB2_stored.sum())
            # TODO: Future development of Stored path here.

            # PATH3
            PB3_reMFG = PBC.mul(df['mod_EOL_pb3_reMFG'].values*0.01)
            df['PB3_reMFG'] = list(PB3_reMFG.sum())

            PB3_reMFG_yield = PB3_reMFG.mul(
                                        df['mod_EOL_reMFG_yield'].values*0.01)
            df['PB3_reMFG_yield'] = list(PB3_reMFG_yield.sum())

            PB3_reMFG_unyield = PB3_reMFG-PB3_reMFG_yield
            df['PB3_reMFG_unyield'] = list(PB3_reMFG_unyield.sum())

            # PATH 4
            PB4_recycled = PBC.mul(df['mod_EOL_pb4_recycled'].values*0.01)
            df['PB4_recycled'] = list(PB4_recycled.sum())

            # ADD Matrices now for path goods and bads, becuase we don't need
            # to distinguish on the source of the material stream.
            P1_landfill = PG1_landfill + PB1_landfill
            P2_stored = PG2_stored + PB2_stored
            P3_reMFG_yield = PG3_reMFG_yield + PB3_reMFG_yield
            P3_reMFG_unyield = PG3_reMFG_unyield + PB3_reMFG_unyield

            df['P2_stored'] = list(P2_stored.sum())

            df['P3_reMFG'] = list((P3_reMFG_yield+P3_reMFG_unyield).sum())

            P4_recycled = PG4_recycled + PB4_recycled
            df['P4_recycled'] = list(P4_recycled.sum())

            # Cleanup of internal renaming and internal use columns
            df.drop(['new_Installed_Capacity_[W]', 't50', 't90'],
                    axis=1, inplace=True)

            # Printout ref. of how much more module area is being manufactured.
            # The manufactured efficiency is calculated on more detail on the
            # material loop below for hte mass.
            df['ModuleTotal_MFG'] = df['Area']*100/df['mod_MFG_eff']

            ################
            # Material Loop#
            ################

            if materials_input is None:
                materials = list(self.scenario[scen].material.keys())           
            else:
                if isinstance(materials_input, str):
                    materials = [materials_input]

            for mat in materials:

                print("==> Working on Material : ", mat)

                dm = self.scenario[scen].material[mat].matdataIn_m.copy()
                initialColsMat = dm.keys()
                # SWITCH TO MASS UNITS FOR THE MATERILA NOW:
                # THIS IS DIFFERENT MULTIPLICATION THAN THE REST
                # BECAUSE IT DEPENDS TO THE ORIGINAL MASS OF EACH MODULE
                # WHEN INSTALLED
                # [M1  * [  G1_1   G1_2    G1_3   G2_4 ...]
                #  M2     [    0    G2_1    G2_2   G2_3 ...]
                #  M3]    [    0      0     G3_1   G3_2 ...]
                #
                #           EQUAL
                # mat_EOL_sentoRecycling =
                #     [  G1_1*M1   G1_2*M1    G1_3*M1   G2_4*M1 ...]
                #     [    0       G2_1*M2    G2_2*M2   G2_3*M2 ...]
                #     [    0           0      G3_1*M3   G3_2*M3 ...]
                #


                dm['mat_L0'] = list(L0.multiply(dm['mat_massperm2'], axis=0).sum())

                dm['mat_PG2_stored'] = list(P2_stored.multiply(dm['mat_massperm2'],axis=0).sum())

                dm['mat_L1'] = list(P1_landfill.multiply(dm['mat_massperm2'], axis=0).sum())

                # PATH 3
                mat_reMFG = P3_reMFG_yield.multiply(dm['mat_massperm2'],axis=0)
                mat_reMFG_mod_unyield = P3_reMFG_unyield.multiply(dm['mat_massperm2'],axis=0)
                dm['mat_reMFG'] = list(mat_reMFG.sum())
                dm['mat_reMFG_mod_unyield'] = list(mat_reMFG_mod_unyield.sum())

                dm['mat_reMFG_target'] = dm['mat_reMFG'] * dm['mat_PG3_ReMFG_target'] * 0.01
                dm['mat_reMFG_untarget'] = dm['mat_reMFG']-dm['mat_reMFG_target']

                dm['mat_reMFG_yield'] = dm['mat_reMFG_target'] * dm['mat_ReMFG_yield'] * 0.01
                dm['mat_reMFG_unyield'] = dm['mat_reMFG_target'] - dm['mat_reMFG_yield']


                # SUBPATH 1: ReMFG to Recycling
                dm['mat_reMFG_all_unyields'] = dm['mat_reMFG_mod_unyield'] + dm['mat_reMFG_untarget'] + dm['mat_reMFG_unyield']
                dm['mat_reMFG_2_recycle'] = dm['mat_reMFG_all_unyields'] * df['mod_EOL_sp_reMFG_recycle'] * 0.01
                dm['mat_L2'] = dm['mat_reMFG_all_unyields']-dm['mat_reMFG_2_recycle']


                # PATH 4
                mat_recycled = P4_recycled.multiply(dm['mat_massperm2'],axis=0)
                dm['mat_recycled_PG4'] = list(mat_recycled.sum())
                dm['mat_recycled_all'] = dm['mat_recycled_PG4'] + dm['mat_reMFG_2_recycle']

                dm['mat_recycled_target'] = dm['mat_recycled_all'] * dm['mat_PG4_Recycling_target'] * 0.01
                dm['mat_L3'] = dm['mat_recycled_all'] - dm['mat_recycled_target']  # material un-target

                dm['mat_recycled_yield'] = dm['mat_recycled_target'] * dm['mat_Recycling_yield'] * 0.01
                dm['mat_L4'] = dm['mat_recycled_target'] - dm['mat_recycled_yield']  # material un-target

                # HQ and OQ reycling paths:
                dm['mat_EOL_Recycled_2_HQ'] = dm['mat_recycled_yield'] * dm['mat_EOL_Recycled_into_HQ'] * 0.01
                dm['mat_EOL_Recycled_2_OQ'] = dm['mat_recycled_yield'] - dm['mat_EOL_Recycled_2_HQ']

                dm['mat_EOL_Recycled_HQ_into_MFG'] = dm['mat_EOL_Recycled_2_HQ'] * dm['mat_EOL_RecycledHQ_Reused4MFG'] * 0.01
                dm['mat_EOL_Recycled_HQ_into_OU'] = dm['mat_EOL_Recycled_2_HQ'] - dm['mat_EOL_Recycled_HQ_into_MFG']


                ## Beginning of Life Calculations Now
                ######################################
                # TODO: Close loop later to reduce MFG step... something. mat_reMFG_yield closing to mat_

                # CHECK
                dm['mat_EnteringModuleManufacturing_total'] = (df['Area'] * dm['mat_massperm2']*100/df['mod_MFG_eff'])
                dm['mat_UsedSuccessfullyinModuleManufacturing'] = (df['Area'] * dm['mat_massperm2'])
                dm['mat_LostinModuleManufacturing'] = dm['mat_EnteringModuleManufacturing_total'] - dm['mat_UsedSuccessfullyinModuleManufacturing']

                dm['mat_EnteringModuleManufacturing_total'] = (df['Area'] * dm['mat_massperm2']*100/df['mod_MFG_eff'])

                # Input from Successful ReMFG to offset Module Manufacturing Material Needs.
                dm['mat_EnteringModuleManufacturing_virgin'] = dm['mat_EnteringModuleManufacturing_total'] - dm['mat_reMFG_yield']
                
                ###################HEATHERS REMFG ATTEMPT
                
                dm['mat_EOL_ReMFG_VAT'] = dm['mat_reMFG_yield'] #make a copy of remfged yield to modify

                carryoverReMFG = True #todo, make sim input?
                
                if carryoverReMFG: #if we are using previous years recovered reMFGing materials
                    reMFGsurplusEndofSim = 0 #init
                    
                    for rn in range(0,len(dm)): #loop over sim years
                        reMFGsurplus = ( dm['mat_EOL_ReMFG_VAT'].loc[rn]- # vat of prev remfg
                                        dm['mat_EnteringModuleManufacturing_total'].loc[rn]) #minus mfging needs CHECK THIS
                        #positive value means surplus
                        if reMFGsurplus > 0: #if surplus
                            if rn == len(dm)-1: #end of simulation condition
                                reMFGsurplusEndofSim = reMFGsurplus
                                print("ReMFG surplus End of Sim for Mat ", mat,
                                      " Scenario ", scen, " = ",
                                      reMFGsurplusEndofSim/1000000, " tonnes.")
                                dm.loc[rn,'mat_EOL_ReMFG_VAT'] -= reMFGsurplus
                            else: #during simulation years
                                dm.loc[rn+1,'mat_EOL_ReMFG_VAT'] += reMFGsurplus #move surplus to next year
                                dm.loc[rn,'mat_EOL_ReMFG_VAT'] -= reMFGsurplus #remove surplus from current year
                    #input from REMFG to offset material
                    dm['mat_EnteringModuleManufacturing_virgin'] = ( 
                        dm['mat_EnteringModuleManufacturing_total']-
                        dm['mat_EOL_ReMFG_VAT'])
                    
                else:
                    #input from REMFG to offset material, modify main data frame
                    dm['mat_EnteringModuleManufacturing_virgin'] = ( 
                        dm['mat_EnteringModuleManufacturing_total']-
                        dm['mat_EOL_ReMFG_VAT'])
                
                #####################################################
                    
                # Material Manufacturing Stage
                dm['mat_Manufacturing_Input'] = dm['mat_EnteringModuleManufacturing_virgin'] / (dm['mat_MFG_eff'] * 0.01)

                # Scrap = Lost to Material manufacturing losses + Module manufacturing losses
                dm['mat_MFG_Scrap'] = (dm['mat_Manufacturing_Input'] - dm['mat_EnteringModuleManufacturing_virgin'] +
                                      dm['mat_LostinModuleManufacturing'])
                dm['mat_MFG_Scrap_Sentto_Recycling'] = dm['mat_MFG_Scrap'] * dm['mat_MFG_scrap_Recycled'] * 0.01


                dm['mat_MFG_Scrap_Landfilled'] = dm['mat_MFG_Scrap'] - dm['mat_MFG_Scrap_Sentto_Recycling']
                dm['mat_MFG_Scrap_Recycled_Successfully'] = (dm['mat_MFG_Scrap_Sentto_Recycling'] *
                                                                 dm['mat_MFG_scrap_Recycling_eff'] * 0.01)
                dm['mat_MFG_Scrap_Recycled_Losses_Landfilled'] = (dm['mat_MFG_Scrap_Sentto_Recycling'] -
                                                                          dm['mat_MFG_Scrap_Recycled_Successfully'])
                dm['mat_MFG_Recycled_into_HQ'] = (dm['mat_MFG_Scrap_Recycled_Successfully'] *
                                                        dm['mat_MFG_scrap_Recycled_into_HQ'] * 0.01)
                dm['mat_MFG_Recycled_into_OQ'] = dm['mat_MFG_Scrap_Recycled_Successfully'] - dm['mat_MFG_Recycled_into_HQ']
                dm['mat_MFG_Recycled_HQ_into_MFG'] = (dm['mat_MFG_Recycled_into_HQ'] *
                                          dm['mat_MFG_scrap_Recycled_into_HQ_Reused4MFG'] * 0.01)
                dm['mat_MFG_Recycled_HQ_into_OU'] = dm['mat_MFG_Recycled_into_HQ'] - dm['mat_MFG_Recycled_HQ_into_MFG']

                dm['mat_EOL_Recycled_VAT'] = dm['mat_EOL_Recycled_HQ_into_MFG']
                
                carryoverVat = True # TODO: Make this a sim input

                if carryoverVat:    #if we are using previous years recycled material to closed loop offset
                    recycledsurplusEndofSim = 0 #init
                    # calculate the difference between mfging req and recycled material availability
                    for rr in range(0, len(dm)): #loop over the the years of existing dm 
                        recycledsurplus = ( dm['mat_MFG_Recycled_HQ_into_MFG'].loc[rr] + #mfg scrap in that year
                                       dm['mat_EOL_Recycled_VAT'].loc[rr] #plus EOL scrap in that year
                                       -dm['mat_Manufacturing_Input'].loc[rr] ) #minus mfging needs
                        # positive value means there is a surplus in that year that needs to be carried to next year
                        if recycledsurplus > 0: # if surplus
                            if rr == len(dm)-1: #end of simulation condition
                                recycledsurplusEndofSim = recycledsurplus
                                print("Recycled surplus End of Sim for Mat ", mat,
                                      " Scenario ", scen, " = ",
                                      recycledsurplusEndofSim/1000000, " tonnes.")
                                
                                dm.loc[rr,'mat_EOL_Recycled_VAT'] -= recycledsurplus
                                
                            else:  #during simulation 
                                dm.loc[rr+1,'mat_EOL_Recycled_VAT'] += ( #add the surplus to the next year's VAT
                                            recycledsurplus)
                                dm.loc[rr, 'mat_EOL_Recycled_VAT'] -= recycledsurplus #remove surplus from current year
                                
                    # Input from Successful Recycling to offset Material
                    # Manufacturing Virgin Needs:
                    dm['mat_Virgin_Stock'] = (dm['mat_Manufacturing_Input'] -
                                              dm['mat_EOL_Recycled_VAT'] -
                                              dm['mat_MFG_Recycled_HQ_into_MFG'])     
                    # This is what goes into OU in the 'else' statement.
                    dm['mat_EOL_Recycled_HQ_into_MFG_notUSED'] = (
                        dm['mat_EOL_Recycled_HQ_into_MFG'] - dm['mat_EOL_Recycled_VAT'])

                    # Have ot think on the recycledendofsimsurplus... 
                else:
                # Input from Successful Recycling to offset Material
                # Manufacturing Virgin Needs:                   
                    dm['mat_Virgin_Stock'] = (dm['mat_Manufacturing_Input'] -
                                          dm['mat_EOL_Recycled_HQ_into_MFG'] -
                                          dm['mat_MFG_Recycled_HQ_into_MFG'])

                    # TO DO: rename 2 to original one, just using it for the 
                    # sanity check
                    dm['mat_MFG_Recycled_HQ_into_OU2'] = dm['mat_MFG_Recycled_HQ_into_OU']

                    dm.loc[dm['mat_Virgin_Stock'] < 0, 'mat_MFG_Recycled_HQ_into_OU2'] = (dm[dm['mat_Virgin_Stock'] < 0]['mat_MFG_Recycled_HQ_into_OU2'] - dm[dm['mat_Virgin_Stock'] < 0]['mat_Virgin_Stock'] )
                    
                    dm.loc[dm['mat_Virgin_Stock']<0, 'mat_Virgin_Stock'] = 0
                    print("VAT carryover material is turned OFF")                   
        
                # Calculate raw virgin needs before mining and refining efficiency losses
                dm['mat_Virgin_Stock_Raw'] = (dm['mat_Virgin_Stock'] * 100 /  dm['mat_virgin_eff'])


                    
                    
                # Add Wastes

                dm['mat_Total_EOL_Landfilled'] = (dm['mat_L0']+  #'mat_modules_NotCollected'] +
                                                  dm['mat_L1']+ # 'mat Path Good Chosen to be Landfilled +
                                                  dm['mat_L2']+ # mat not reMFG (yields module, target, or yieldds matr) NOT sent to recycling
                                                  dm['mat_L3']+ # mat in recycling not TARGET so landfilled +
                                                  dm['mat_L4']) # mat in EOL_Recycled_Losses_Landfilled

                dm['mat_Total_MFG_Landfilled'] = (dm['mat_MFG_Scrap_Landfilled'] +
                                                 dm['mat_MFG_Scrap_Recycled_Losses_Landfilled'])

                dm['mat_Total_Landfilled'] = (dm['mat_Total_EOL_Landfilled'] +
                                              dm['mat_Total_MFG_Landfilled'])

                dm['mat_Total_Recycled_OU'] = (dm['mat_EOL_Recycled_2_OQ'] +
                                               dm['mat_EOL_Recycled_HQ_into_OU'] +
                                               dm['mat_MFG_Recycled_into_OQ'] +
                                               dm['mat_MFG_Recycled_HQ_into_OU'])


                self.scenario[scen].material[mat].matdataOut_m = dm[dm.columns.difference(initialColsMat)]


            # CLEANUP MATRICES HERE:
            if debugflag:
                debugdf = df[(list(df.filter(regex='EOL_PG_Year_')))]
                debugdfB = df[(list(df.filter(regex='EOL_L0_Year_')))]
                debugdfC = df[(list(df.filter(regex='EOL_BS_Year')))]
                debugdf = debugdf.join(debugdfB) 
                debugdf = debugdf.join(debugdfC) 
                self.scenario[scen].dataDebug_m = debugdf                        

            df = df[df.columns.drop(list(df.filter(regex='EOL_PG_Year_')))]
            df = df[df.columns.drop(list(df.filter(regex='EOL_L0_Year_')))]
            df = df[df.columns.drop(list(df.filter(regex='EOL_BS_Year')))]

            self.scenario[scen].dataOut_m = df[df.columns.difference(initialCols)]


    #method to calculate energy flows as a function of mass flows and circular pathways
    def calculateEnergyFlow(self, scenarios=None, materials_input=None,
                            insolation = 4800, PR = 0.85):
        '''
        Function takes as input PV ICE resulting mass flow dataframes for scenarios
        and materials and performs the energy flow calculations.

        Parameters
        ------------
        scenarios : None
            string with the scenario name or list of strings with
            scenarios names to loop over. Must exist on the PV ICE object and
            already have undergone the mass flow calculations.
        materials : None
            string with the material name or list of strings with the
            materials names to loop over. Must exists on the PV ICE object
            scenario(s) modeled and already have undergone the mass flow
            calculations.
        insolation : float
            Insolation received in the location modeled during the time period
            modeled. i.e. for 1 year, the average insolation in the US is
            4800 Wh/m2-year. Used to calculate energy-out of the system
            from the installed capacity calculated in the mass flows which already
            considers degradation and decommissions from the fleet.
        PR : float
            Performance ratio, converts from DC to AC accounting for interver
            loading, necessary for EROI. Default is 0.85

        Returns
        --------
        de: dataframe
            Dataframe with columns for each process's energy by year (row).
            Among other columns, ''e_out_annual_[Wh]' reflects the
            energy generation or 'out' of the scenario, such that
            e_out_annual_[Wh] = Insolation * ActivePower/Irradience * time * PR
            time being 365 days for 1 year simulations.
        de_cum: dataframe
            Dataframe with columns for each process's cumulative energy by year (row)
        '''

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        print("\n\n>>>> Calculating Energy Flows <<<<\n")

        for scen in scenarios:
            print("Working on Scenario: ", scen)
            print("********************")
            
            df = self.scenario[scen].dataOut_m
            df_in = self.scenario[scen].dataIn_m
            modEnergy=self.scenario[scen].dataIn_e

            de = pd.DataFrame()
            de['mod_MFG'] = df['ModuleTotal_MFG']*modEnergy['e_mod_MFG']
            de['mod_Install'] = df['Area']*modEnergy['e_mod_Install']
            de['mod_OandM'] = df['Cumulative_Active_Area']*modEnergy['e_mod_OandM']
            de['mod_Repair'] = df['Repaired_Area']*modEnergy['e_mod_Repair']
            de['mod_Demount'] = (df['Resold_Area']+df['Yearly_Sum_Area_PathsBad']+df['Landfill_0_ProjLife']
                               +df['Yearly_Sum_Area_PathsGood'])*modEnergy['e_mod_Demount']
            de['mod_Store'] = df['P2_stored']*modEnergy['e_mod_Store']
            de['mod_Resell_Certify'] = df['Resold_Area']*modEnergy['e_mod_Resell_Certify']
            de['mod_ReMFG_Disassembly'] = df['P3_reMFG']*modEnergy['e_mod_ReMFG_Disassembly']
            de['mod_Recycle_Crush'] = df['P4_recycled']*modEnergy['e_mod_Recycle_Crush']

            #Energy Generation, Energy_out = Insolation (adjusted for bifi) * ActivePower/Irradience * time * PR
            de['e_out_annual_[Wh]'] = insolation*(df['irradiance_stc']/1000) * (df['Effective_Capacity_[W]']/1000) * 365 * PR
            
            self.scenario[scen].dataOut_e = de #Wh
            
            if materials_input is None:
                materials = list(self.scenario[scen].material.keys())
            else:
                if isinstance(materials_input, str):
                    materials = [materials_input]
                    
            for mat in materials:
                
                if self.scenario[scen].material[mat].matdataIn_e is None:
                    print("==> No energy material found for Material : ", mat, ". Skipping Energy calculations.")
                    demat = None
                else:
    
                    print("==> Working on Energy for Material : ", mat)
                    
                    dm = self.scenario[scen].material[mat].matdataOut_m               
                    matEnergy=self.scenario[scen].material[mat].matdataIn_e
        
                    demat = pd.DataFrame()
                    demat['mat_extraction'] = dm['mat_Virgin_Stock_Raw']*matEnergy['e_mat_extraction']
                    demat['mat_MFG_virgin'] = dm['mat_Virgin_Stock']*matEnergy['e_mat_MFG'] #multiply only the virgin input
                    demat['mat_MFG_virgin_fuel'] = demat['mat_MFG_virgin']*matEnergy['e_mat_MFG_fuelfraction']*0.01 #fuel fraction of the virgin energy demands
                    #demat['mat_MFG_virgin_elec'] = demat['mat_MFG_virgin']*(1-matEnergy['e_mat_MFG_fuelfraction'])*0.01 
                    demat['mat_MFGScrap_LQ'] = dm['mat_MFG_Scrap_Sentto_Recycling']*matEnergy['e_mat_MFGScrap_LQ'] #OQ only - everything that goes into mfgscrap recycle
                    demat['mat_MFGScrap_HQ'] = dm['mat_MFG_Recycled_into_HQ']*(matEnergy['e_mat_MFGScrap_HQ']) #the additional energy required for HQ
                    demat['mat_MFGScrap_HQ_fuel'] = demat['mat_MFGScrap_HQ']*matEnergy['e_mat_Recycled_HQ_fuelfraction']*0.01 #fraction of HQ energy attributable to fuel
                    #demat['mat_MFG_virgin_elec'] = demat['mat_MFG_virgin']*(1-matEnergy['e_mat_MFG_fuelfraction'])*0.01 
    
                    demat['mat_Landfill'] = dm['mat_Total_Landfilled']*matEnergy['e_mat_Landfill']
                    demat['mat_Landfill_fuel'] = demat['mat_Landfill']*matEnergy['e_mat_Landfill_fuelfraction']*0.01 #fuel fraction of landfilling
                    demat['mat_EoL_ReMFG_clean'] = dm['mat_reMFG_target']*matEnergy['e_mat_EoL_ReMFG_clean']
                    demat['mat_Recycled_LQ'] = dm['mat_recycled_target']*matEnergy['e_mat_Recycled_LQ']
                    demat['mat_Recycled_HQ'] = dm['mat_EOL_Recycled_2_HQ']*matEnergy['e_mat_Recycled_HQ']
                    demat['mat_Recycled_HQ_fuel'] = demat['mat_Recycled_HQ']*matEnergy['e_mat_Recycled_HQ_fuelfraction']*0.01
                    demat['mat_Recycled_HQ_elec'] = demat['mat_Recycled_HQ']-demat['mat_Recycled_HQ_fuel']
    
                self.scenario[scen].material[mat].matdataOut_e = demat #Wh

    def calculateCarbonFlows(self, scenarios=None, materials_input=None, 
                             countrygridmixes = None, gridemissionfactors = None, 
                             materialprocesscarbon = None, modulecountrymarketshare = None, 
                             materialcountrymarketshare = None, country_deploy = 'USA'):
        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]



        print("\n\n>>>> Calculating Carbon Flows <<<<\n")
        
        #carbon folder 
        #TODO: NEED TO MAKE THIS MORE DYNAMIC/robust
        carbonfolder = Path(DATA_PATH) / 'CarbonLayer'
        
        if countrygridmixes is None:
            countrygridmixes_full = pd.read_csv(os.path.join(carbonfolder,'baseline2100_countrygridmix.csv'))#1995-2100
        else:
            if isinstance(countrygridmixes, str):
                countrygridmixes_full = pd.read_csv(countrygridmixes)
            if isinstance(countrygridmixes_full, object):
                countrygridmixes_full = countrygridmixes_full
        
        #default files
        gridemissionfactors = pd.read_csv(os.path.join(carbonfolder,'baseline_electricityemissionfactors.csv')) #no date
        materialprocesscarbon = pd.read_csv(os.path.join(carbonfolder,'baseline_materials_processCO2.csv'), index_col='Material') #no date
        #countrygridmixes = pd.read_csv(os.path.join(carbonfolder,'baseline_countrygridmix.csv')) #2000-2050 or 2100
        countrymodmfg_full = pd.read_csv(os.path.join(carbonfolder,'baseline_module_countrymarketshare.csv')) #1995-2100
        
        
        
        for scen in scenarios:
            print("Working on Scenario: ", scen)
            print("********************")
        
            #df = self.scenario[scen].dataOut_m
            #df_in = self.scenario[scen].dataIn_m
            de = self.scenario[scen].dataOut_e
            #de_in = self.scenario[scen].dataIn_e
            
            #select years of carbon data to use in calc based on scen out of 1995-2100
            scenStartYear = int(self.scenario[scen].dataIn_m.iloc[0]['year'])
            scenEndYear = int(self.scenario[scen].dataIn_m.iloc[-1]['year'])
            
            countrymodmfg = countrymodmfg_full[(countrymodmfg_full.iloc[:,0]>=scenStartYear) & (countrymodmfg_full.iloc[:,0]<=scenEndYear)]
            countrygridmixes = countrygridmixes_full[(countrygridmixes_full.iloc[:,0]>=scenStartYear) & (countrygridmixes_full.iloc[:,0]<=scenEndYear)]
            countrymodmfg.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
            countrygridmixes.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
            
            #carbon intensity of country grid mixes
            #extract lists
            countryfuellist = [cols.split('_')[0] for cols in countrygridmixes.columns[1:]]
            countrylist = (pd.DataFrame(countryfuellist)[0].unique()).tolist()
            countryfuellist_fuels = [cols.split('_')[1] for cols in countrygridmixes.columns[1:]]
            fuellist = (pd.DataFrame(countryfuellist_fuels)[0].unique()).tolist()
            
            #create carbon intensity of country grid mix, 
            #inside scenarios allows for different future grid projections
            final_country_carbon_int = []
            for country in countrylist:
                temp_country_carbon = []
                for fuel in fuellist: 
                    fuelemitfactor = gridemissionfactors[gridemissionfactors['Energy Source']==fuel]['CO2eq_gpWh_IPCC2006']
                    #print(fuelemitfactor)
                    fuelemitfactor = list(fuelemitfactor)[0]
                    if str(country+'_'+fuel) in countrygridmixes:
                        countryfuel = countrygridmixes[str(country+'_'+fuel)]
                        temp_country_carbon.append(list(0.01*countryfuel*fuelemitfactor)) #multiply country fuel % by fuel factor
                final_country_carbon_int.append(list(pd.DataFrame(temp_country_carbon).sum())) #sum the carbon int by country

            country_carbonpwh = pd.DataFrame(final_country_carbon_int).T
            country_carbonpwh.columns = countrylist
            
            #carbon intensity of module manufacturing weighted by country
            #list countries mfging modules
            print('Working on Carbon for Module')
            countriesmfgingmodules = list(countrymodmfg.columns[1:])

            #weight carbon intensity of electricity by countries which mfging modules
            countrycarbon_modmfg_gco2eqpwh = []
            for country in countriesmfgingmodules:
                if country in country_carbonpwh:
                    currentcountry = country_carbonpwh[country]*countrymodmfg[country]*.01
                    countrycarbon_modmfg_gco2eqpwh.append(currentcountry)
                else: print(country)
        
            modmfg_gco2eqpwh_bycountry = pd.DataFrame(countrycarbon_modmfg_gco2eqpwh).T #
            modmfg_gco2eqpwh_bycountry['Global_gCO2eqpwh'] = modmfg_gco2eqpwh_bycountry.sum(axis=1) #annual carbon intensity of pv module mfg wtd by country
            #print(modmfg_gco2eqpwh_bycountry['China'].iloc[-1])
            #carbon impacts module mfging wtd by country
            dc = modmfg_gco2eqpwh_bycountry.mul(de['mod_MFG'], axis=0)
            dc.rename(columns={'Global_gCO2eqpwh':'Global'}, inplace=True)
            dc = dc.add_suffix('_mod_MFG_gCO2eq')
            
            #carbon impacts other module level steps
            #assumption: all CO2 after mfg is attributable to target deployment country
            country_deploy = 'USA' #user input in calc carbon function, default USA
            dc['mod_Install_gCO2eq'] = de['mod_Install']*country_carbonpwh[country_deploy]
            dc['mod_OandM_gCO2eq'] = de['mod_OandM']*country_carbonpwh[country_deploy]
            dc['mod_Repair_gCO2eq'] = de['mod_Repair']*country_carbonpwh[country_deploy]
            dc['mod_Demount_gCO2eq'] = de['mod_Demount']*country_carbonpwh[country_deploy]
            dc['mod_Store_gCO2eq'] = de['mod_Store']*country_carbonpwh[country_deploy]
            dc['mod_Resell_Certify_gCO2eq'] = de['mod_Resell_Certify']*country_carbonpwh[country_deploy]
            dc['mod_ReMFG_Disassembly_gCO2eq'] = de['mod_ReMFG_Disassembly']*country_carbonpwh[country_deploy]
            dc['mod_Recycle_Crush_gCO2eq'] = de['mod_Recycle_Crush']*country_carbonpwh[country_deploy]
            
            self.scenario[scen].dataOut_c = dc
            
            if materials_input is None:
                materials = list(self.scenario[scen].material.keys())
            else:
                if isinstance(materials_input, str):
                    materials = [materials_input]
            
            for mat in materials:
                
                if self.scenario[scen].material[mat].matdataIn_e is None:
                    print("==> No Carbon intensity found for Material : ", mat, ". Skipping Carbon calculations.")
                    demat = None
                else:
    
                    print("==> Working on Carbon for Material : ", mat)
                    
                    demat = self.scenario[scen].material[mat].matdataOut_e
                    dm = self.scenario[scen].material[mat].matdataOut_m               
                    
                    matfilename = 'baseline_'+str(mat)+'_MFGing_countrymarketshare.csv' #1995-2100
                    countrymatmfg_full = pd.read_csv(os.path.join(carbonfolder, matfilename))
                    
                    #trim to scenario years
                    countrymatmfg = countrymatmfg_full[(countrymatmfg_full.iloc[:,0]>=scenStartYear) & (countrymatmfg_full.iloc[:,0]<=scenEndYear)]
                    countrymatmfg.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
                
                    #carbon intensity of material manufacturing weighted by country
                    #list countries mfging material
                    countriesmfgingmat = list(countrymatmfg.columns[1:])

                    #weight carbon intensity of electricity by countries which mfging modules
                    countrycarbon_matmfg_gco2eqpwh = []
                    for matcountry in countriesmfgingmat:
                        if matcountry in country_carbonpwh:
                            currentcountry = country_carbonpwh[matcountry]*countrymatmfg[matcountry]*.01
                            countrycarbon_matmfg_gco2eqpwh.append(currentcountry)
                        else: print('Check '+mat+' MFGing by Country file OR add to country grid mix file. We dont have a grid mix for: '+matcountry)
        
                    matmfg_gco2eqpwh_bycountry = pd.DataFrame(countrycarbon_matmfg_gco2eqpwh).T #
                    matmfg_gco2eqpwh_bycountry['Global_gCO2eqpwh'] = matmfg_gco2eqpwh_bycountry.sum(axis=1) #annual carbon intensity of elec country wtd 
            
                    #carbon impacts mat mfging wtd by country
                    #electric
                    demat['mat_MFG_virgin_elec'] = demat['mat_MFG_virgin']-demat['mat_MFG_virgin_fuel']
                    dcmat = matmfg_gco2eqpwh_bycountry.mul(demat['mat_MFG_virgin_elec'],axis=0)
                    dcmat.rename(columns={'Global_gCO2eqpwh':'Global'}, inplace=True)
                    dcmat = dcmat.add_suffix('_vmfg_elec_gCO2eq')
                    
                    #fuel CO2 impacts
                    steamHeat = list(gridemissionfactors[gridemissionfactors['Energy Source']=='SteamAndHeat']['CO2_gpWh_EPA'])[0]
                    dcmat['mat_vmfg_fuel_gCO2eq'] = demat['mat_MFG_virgin_fuel']*steamHeat #CO2 from mfging fuels
                    dcmat['mat_MFGScrap_HQ_fuel_gCO2eq'] = demat['mat_MFGScrap_HQ_fuel']*steamHeat #CO2 from mfging scrap recycling fuels
                    dcmat['mat_landfill_fuel_gCO2eq'] = demat['mat_Landfill_fuel']*steamHeat
                    dcmat['mat_Recycled_HQ_fuel_gCO2eq'] = demat['mat_Recycled_HQ_fuel']*steamHeat #co2 from eol recycling fuels
                    
                    #circular paths electricity in target country
                    dcmat['mat_landfill_elec_gCO2eq'] = (demat['mat_Landfill']-demat['mat_Landfill_fuel'])*country_carbonpwh[country_deploy]
                    dcmat['mat_EoL_ReMFG_clean_elec_gCO2eq'] = demat['mat_EoL_ReMFG_clean']*country_carbonpwh[country_deploy]
                    dcmat['mat_Recycled_LQ_elec_gCO2eq'] = demat['mat_Recycled_LQ']*country_carbonpwh[country_deploy]
                    dcmat['mat_Recycled_HQ_elec_gCO2eq'] = demat['mat_Recycled_HQ_elec']*country_carbonpwh[country_deploy]
                    
                    #CO2 process emissions from MFGing (v, lq, hq)
                    #mass of material being processed in each stream * CO2 intensity of that process
                    dcmat['mat_vMFG_p_gCO2eq'] = dm['mat_Virgin_Stock']*materialprocesscarbon.loc[mat,'v_MFG_gCO2eqpg']
                    dcmat['mat_LQmfg_p_gCO2eq'] = dm['mat_MFG_Scrap_Sentto_Recycling']*materialprocesscarbon.loc[mat,'LQ_Recycle_gCO2eqpg']
                    dcmat['mat_LQeol_p_gCO2eq'] = dm['mat_recycled_target']*materialprocesscarbon.loc[mat,'LQ_Recycle_gCO2eqpg']
                    #dcmat['mat_LQ_p_gCO2eq'] = dcmat['mat_LQmfg_p_gCO2eq']+dcmat['mat_LQeol_p_gCO2eq']
                    dcmat['mat_HQmfg_p_gCO2eq'] = dm['mat_MFG_Recycled_into_HQ']*materialprocesscarbon.loc[mat,'HQ_Recycle_gCO2eqpg']
                    dcmat['mat_HQeol_p_gCO2eq'] = dm['mat_EOL_Recycled_2_HQ']*materialprocesscarbon.loc[mat,'HQ_Recycle_gCO2eqpg']
                    #dcmat['mat_HQ_p_gCO2eq'] = dcmat['mat_HQmfg_p_gCO2eq']+dcmat['mat_HQeol_p_gCO2eq'] 
                
                    #sum carbon stuff
                    #dcmat['mat_vMFG_energy_gCO2eq'] = dcmat['Global_vmfg_elec_gCO2eq']+dcmat['mat_vmfg_fuel_gCO2eq']
                    #dcmat['mat_vMFG_total_gCO2eq'] = dcmat['mat_vMFG_energy_gCO2eq']+dcmat['mat_vMFG_p_gCO2eq']
                    #dcmat['mat_Recycle_e_p_gCO2eq'] = dcmat['mat_HQ_p_gCO2eq'] + dcmat['mat_LQ_p_gCO2eq'] + dcmat['mat_MFGScrap_HQ_fuel_gCO2eq']+dcmat['mat_Recycled_LQ_gCO2eq']+dcmat['mat_Recycled_HQ_elec_gCO2eq']
                    #dcmat['mat_landfill_total_gCO2eq'] = dcmat['mat_landfill_elec_gCO2eq'] + dcmat['mat_landfill_fuel_gCO2eq']
                
                    self.scenario[scen].material[mat].matdataOut_c = dcmat
                
    def scenMod_IRENIFY(self, scenarios=None, ELorRL='RL'):

        if ELorRL == 'RL':
            weibullInputParams = {'alpha': 5.3759, 'beta': 30}  # Regular-loss scenario IRENA
            print("Using Irena Regular Loss Assumptions")
        if ELorRL == 'EL':
            weibullInputParams = {'alpha': 2.4928, 'beta': 30}  # Regular-loss scenario IRENA
            print("Using Irena Early Loss Assumptions")

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        for scen in scenarios:
            self.scenario[scen].dataIn_m['weibull_alpha'] = weibullInputParams['alpha']
            self.scenario[scen].dataIn_m['weibull_beta'] = weibullInputParams['beta']
            self.scenario[scen].dataIn_m['mod_lifetime'] = 40.0
            self.scenario[scen].dataIn_m['mod_MFG_eff'] = 100.0

            for mat in self.scenario[scen].material:
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_eff'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled'] = 0.0

        return


    def check_Years_dataandMaterials(self, scenarios=None, materials=None):
        '''
        '''
        print ("Not Done")

    def trim_Years( self, startYear, endYear, aggregateInstalls=False,
                   averageEfficiency=False, averagemassdata = False, methodAddedYears='repeat',
                   scenarios=None, materials=None):
        '''
        This function now just trims years at the start or end
        
        methodStart : str
            'trim' or 'aggregate'. Trim cuts the values before the year specified.
            Aggregate sums the values (if any) up to the year specified and sets it
            in that year. No backfilling of data enabled at the moment.
        methodEnd : str
            'repeat' or 'zeroes' only options at the moment.
            'repeat' Increases to the endYear by repeating the last value.
            zeroes places zeroes.

        '''

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        scen0 = scenarios[0] #static scenario of the first in the list
        dataStartYear = int(self.scenario[scen0].dataIn_m.iloc[0]['year'])
        dataEndYear = int(self.scenario[scen0].dataIn_m.iloc[-1]['year'])

        tryenergy = True #see below, default to try trimming energy dfs
        for scen in scenarios:
            print('Trimming and extending ',scen)
            baseline = self.scenario[scen].dataIn_m
            # Add check if data does not need to be reduced to not do these.
            reduced = baseline.loc[(baseline['year']>=startYear) & (baseline['year']<=endYear)].copy()
            reduced.reset_index(drop=True, inplace=True)
            self.scenario[scen].dataIn_m = reduced #reassign the material data to the simulation
            
            if int(endYear) > int(dataEndYear): # extend data with start trimming
                lengthtoadd = int(endYear) - int(dataEndYear)
                newIndex = pd.RangeIndex(0,lengthtoadd,1) #create a new index to append
                add = pd.DataFrame(columns=baseline.columns, index=newIndex) #create empty df, using new index
                extended = pd.concat([reduced,add]) #concat the trimmed early years with the new extended years
                #reset the index and forward fill the last values
                extended.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
                extended.ffill(inplace=True) #forward fill columns
                # fix years
                newYears = pd.Series(range(dataEndYear+1,endYear+1,1)) #create a series of years to overwrite the ffill
                extended.loc[len(reduced):,'year'] = newYears.values
                
                self.scenario[scen].dataIn_m = extended #reassign to the simulation

            if aggregateInstalls:
                prev = baseline.loc[(baseline['year']<startYear)].sum()
                reduced.loc[reduced['year'] == startYear, 'new_Installed_Capacity_[MW]'] = prev['new_Installed_Capacity_[MW]']

            if averageEfficiency:
                prev = baseline.loc[(baseline['year']<startYear)].mean()
                reduced.loc[reduced['year'] == startYear, 'mod_eff'] = prev['mod_eff']

            if tryenergy: # I'm sure theres a more elegant way to check if a dataframe exists.
                
                try:
                    baseline = self.scenario[scen].dataIn_e
    
                    # Add check if data does not need to be reduced to not do these.
                    reduced = baseline.loc[(baseline['year']>=startYear) & (baseline['year']<=endYear)].copy()
                    reduced.reset_index(drop=True, inplace=True)
                    self.scenario[scen].dataIn_e = reduced #reassign the material data to the simulation
                    
                    if int(endYear) > int(dataEndYear): # extend data with start trimming
                        lengthtoadd = int(endYear) - int(dataEndYear)
                        newIndex = pd.RangeIndex(0,lengthtoadd,1) #create a new index to append
                        add = pd.DataFrame(columns=baseline.columns, index=newIndex) #create empty df, using new index
                        extended = pd.concat([reduced,add]) #concat the trimmed df with the new extended years
                        
                        extended.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
                        extended.ffill(inplace=True) #forward fill columns
                        # fix years
                        newYears = pd.Series(range(dataEndYear+1,endYear+1,1)) #create a series of years to overwrite the ffill
                        extended.loc[len(reduced):,'year'] = newYears.values
                        #print(extended.tail(5))
                        self.scenario[scen].dataIn_e = extended #reassign to the simulation
                    
                    if aggregateInstalls:
                        print("Warning: Attempting to aggregate Installs for "+ 
                              "triming years for Energy Data. This is not yet "+
                              "implemented, it will just clip data to years "+
                              "selected. Let silvana know this feature is "+
                              "actually needed so she works on it.")
                    if averageEfficiency:
                        print("Warning: Attempting to averageEfficiency for "+
                              "triming years for Energy Data. This is not yet "+
                              "implemented, it will just clip data to years "+
                              "selected. Let silvana know this feature is "+
                              "actually needed so she works on it.")

                    
                except:
                    print("No energy data loaded. Skipping for all next scenarios and materials")
                    tryenergy = False
                    
            
            for mat in self.scenario[scen].material:

                matdf = self.scenario[scen].material[mat].matdataIn_m #pull out the df
                reduced = matdf.loc[(matdf['year']>=startYear) & (matdf['year']<=endYear)].copy()
                reduced.reset_index(drop=True, inplace=True)
                self.scenario[scen].material[mat].matdataIn_m = reduced #reassign the material data to the simulation
                
                if int(endYear) > int(dataEndYear): # extend data with start trimming
                    lengthtoadd = int(endYear) - int(dataEndYear)
                    newIndex = pd.RangeIndex(0,lengthtoadd,1) #create a new index to append
                    add = pd.DataFrame(columns=baseline.columns, index=newIndex) #create empty df, using new index
                    extended = pd.concat([reduced,add]) #concat the trimmed early years with the new extended years
                    extended.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
                    extended.ffill(inplace=True) #forward fill columns
                    # fix years
                    newYears = pd.Series(range(dataEndYear+1,endYear+1,1)) #create a series of years to overwrite the ffill
                    extended.loc[len(reduced):,'year'] = newYears.values
                    
                    #print(extended.tail(5))
                    self.scenario[scen].material[mat].matdataIn_m = extended #reassign to the simulation
                
                if averagemassdata == 'average':
                    prev = matdf.loc[(baseline['year']<startYear)].mean()
                    matkeys = list(reduced.keys())[1:12]
                    for matkey in matkeys: # skipping year (0). Skipping added columsn from mass flow
                        reduced.loc[reduced['year'] == startYear, matkey] = prev[matkey]



                if tryenergy: # I'm sure theres a more elegant way to check if a dataframe exists.
    
                    try:
                        matdf = self.scenario[scen].material[mat].matdataIn_e #pull out the df
                        reduced = matdf.loc[(matdf['year']>=startYear) & (matdf['year']<=endYear)].copy()
                        reduced.reset_index(drop=True, inplace=True)
                        self.scenario[scen].material[mat].matdataIn_e = reduced #reassign the material data to the simulation
                        if int(endYear) > int(dataEndYear): # extend data with start trimming
                            lengthtoadd = int(endYear) - int(dataEndYear)
                            newIndex = pd.RangeIndex(0,lengthtoadd,1) #create a new index to append
                            add = pd.DataFrame(columns=baseline.columns, index=newIndex) #create empty df, using new index
                            extended = pd.concat([reduced,add]) #concat the trimmed early years with the new extended years
                            extended.reset_index(inplace=True, drop=True) #reset the index and don't include the old in new df
                            extended.ffill(inplace=True) #forward fill columns
                            # fix years
                            newYears = pd.Series(range(dataEndYear+1,endYear+1,1)) #create a series of years to overwrite the ffill
                            extended.loc[len(reduced):,'year'] = newYears.values
        
                            #print(extended.tail(5))
                            self.scenario[scen].material[mat].matdataIn_e = extended #reassign to the simulation
                            
                        if averagemassdata == 'average':
                            print("Warning: Attempting to averagemassdata for "+
                                  "triming years for Energy Data. This is not yet "+
                                  "implemented, it will just clip data to years "+
                                  "selected. Let silvana know this feature is "+
                                  "actually needed so she works on it.")
    
                        #consistent year check
                        newStartYear_e = int(self.scenario[scen].dataIn_e.iloc[0]['year'])
                        newEndYear_e = int(self.scenario[scen].dataIn_e.iloc[-1]['year'])
                        newStartYear_emat = int(self.scenario[scen].material[mat].matdataIn_e.iloc[0]['year'])
                        newEndYear_emat = int(self.scenario[scen].material[mat].matdataIn_e.iloc[-1]['year'])
                        if (newStartYear_e == newStartYear_emat) & (newEndYear_e == newEndYear_emat):
                            print(scen,mat,": Data trimmed for Energy, years now encompass ", newStartYear_e, " to ", newEndYear_e) #modify to recheck the new data start and end year, because currently can specify a later year and it wont extend
                        else:
                            print('There is an issue with year modification for Energy')
                    except:
                        print("No material energy data loaded.")
            #consistent year check
            newStartYear_m = int(self.scenario[scen].dataIn_m.iloc[0]['year'])
            newEndYear_m = int(self.scenario[scen].dataIn_m.iloc[-1]['year'])
            newStartYear_mat = int(self.scenario[scen].material[mat].matdataIn_m.iloc[0]['year'])
            newEndYear_mat = int(self.scenario[scen].material[mat].matdataIn_m.iloc[-1]['year'])
            if (newStartYear_m == newStartYear_mat) & (newEndYear_m == newEndYear_mat):
                print(scen,mat,": Data trimmed for Mass, years now encompass ", newStartYear_m, " to ", newEndYear_m) #modify to recheck the new data start and end year, because currently can specify a later year and it wont extend
            else:
                print('There is an issue with year modification for Mass!!')
            

    def scenMod_IRENIFY(self, scenarios=None, ELorRL='RL'):

        if ELorRL == 'RL':
            weibullInputParams = {'alpha': 5.3759, 'beta': 30}  # Regular-loss scenario IRENA
            print("Using Irena Regular Loss Assumptions")
        if ELorRL == 'EL':
            weibullInputParams = {'alpha': 2.4928, 'beta': 30}  # Regular-loss scenario IRENA
            print("Using Irena Early Loss Assumptions")

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        for scen in scenarios:
            self.scenario[scen].dataIn_m['weibull_alpha'] = weibullInputParams['alpha']
            self.scenario[scen].dataIn_m['weibull_beta'] = weibullInputParams['beta']
            self.scenario[scen].dataIn_m['mod_lifetime'] = 40.0
            self.scenario[scen].dataIn_m['mod_MFG_eff'] = 100.0

            for mat in self.scenario[scen].material:
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_eff'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled'] = 0.0

        return



    def scenMod_PerfectManufacturing(self, scenarios=None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        for scen in scenarios:
            self.scenario[scen].dataIn_m['mod_MFG_eff'] = 100.0

            for mat in self.scenario[scen].material:
                self.scenario[scen].material[mat].matdataIn_m['mat_virgin_eff'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_eff'] = 100.0
        return

    def scenMod_noCircularity(self, scenarios=None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        for scen in scenarios:
            self.scenario[scen].dataIn_m['mod_EOL_collection_eff'] = 0.0 #this should send all to landfill, but just in case set rest to 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg0_resell'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg1_landfill'] = 100.0 #all to landfill
            self.scenario[scen].dataIn_m['mod_EOL_pg2_stored'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg3_reMFG'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg4_recycled'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_sp_reMFG_recycle'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pb1_landfill'] = 100.0 #all to landfill
            self.scenario[scen].dataIn_m['mod_EOL_pb2_stored'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pb3_reMFG'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pb4_recycled'] = 0.0
            self.scenario[scen].dataIn_m['mod_Repair'] = 0.0
            self.scenario[scen].dataIn_m['mod_MerchantTail'] = 0.0 #should this one be set to 0?
            
            

            for mat in self.scenario[scen].material:
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycling_eff'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled_into_HQ'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled_into_HQ_Reused4MFG'] = 0.0

                self.scenario[scen].material[mat].matdataIn_m['mat_PG3_ReMFG_target'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_PG4_Recycling_target'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_Recycling_yield'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_EOL_Recycled_into_HQ'] = 0.0
                self.scenario[scen].material[mat].matdataIn_m['mat_EOL_RecycledHQ_Reused4MFG'] = 0.0


        return
    
    def scenMod_perfectRecycling(self, scenarios=None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        for scen in scenarios:
            self.scenario[scen].dataIn_m['mod_EOL_collection_eff'] = 100.0 #this should send all to landfill, but just in case set rest to 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg0_resell'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg1_landfill'] = 0.0 #all to landfill
            self.scenario[scen].dataIn_m['mod_EOL_pg2_stored'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg3_reMFG'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pg4_recycled'] = 100.0
            self.scenario[scen].dataIn_m['mod_EOL_sp_reMFG_recycle'] = 100.0
            self.scenario[scen].dataIn_m['mod_EOL_pb1_landfill'] = 0.0 #all to landfill
            self.scenario[scen].dataIn_m['mod_EOL_pb2_stored'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pb3_reMFG'] = 0.0
            self.scenario[scen].dataIn_m['mod_EOL_pb4_recycled'] = 100.0
            self.scenario[scen].dataIn_m['mod_Repair'] = 0.0
            self.scenario[scen].dataIn_m['mod_MerchantTail'] = 0.0 #should this one be set to 0?
            
            

            for mat in self.scenario[scen].material:
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycling_eff'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled_into_HQ'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_MFG_scrap_Recycled_into_HQ_Reused4MFG'] = 100.0

                self.scenario[scen].material[mat].matdataIn_m['mat_PG3_ReMFG_target'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_PG4_Recycling_target'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_Recycling_yield'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_EOL_Recycled_into_HQ'] = 100.0
                self.scenario[scen].material[mat].matdataIn_m['mat_EOL_RecycledHQ_Reused4MFG'] = 100.0


        return

    def aggregateResults(self, scenarios=None, materials_input=None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        keywds = ['mat_Virgin_Stock', 'mat_Total_Landfilled', 'mat_Total_EOL_Landfilled', 'mat_Total_MFG_Landfilled']
        nice_keywds = ['VirginStock', 'WasteAll', 'WasteEOL', 'WasteMFG']

        USyearly=pd.DataFrame()

        for scen in scenarios:
            for ii in range(len(keywds)):
                keywd = keywds[ii]
                nicekey = nice_keywds[ii]


                if materials_input is None:
                    materials = list(self.scenario[scen].material.keys())
                else:
                    if isinstance(materials_input, str):
                        materials = [materials_input]

                for mat in materials:
                    USyearly[nicekey+'_'+mat+'_'+self.name+'_'+scen] = self.scenario[scen].material[mat].matdataOut_m[keywd]
                filter_col = [col for col in USyearly if (col.startswith(nicekey) and col.endswith(self.name+'_'+scen)) ]
                USyearly[nicekey+'_Module_'+self.name+'_'+scen] = USyearly[filter_col].sum(axis=1)
                # 2DO: Add multiple objects option


        USyearly = USyearly/1000000  # This is the ratio for grams to Metric tonnes
        USyearly = USyearly.add_suffix('_[Tonnes]')

        # Different units, so no need to do the ratio to Metric tonnes :p
        keywd1='new_Installed_Capacity_[MW]'

        for scen in scenarios:
            USyearly['newInstalledCapacity_'+self.name+'_'+scen+'_[MW]'] = self.scenario[scen].dataIn_m[keywd1]

        # Creating c umulative results
        UScum = USyearly.copy()
        UScum = UScum.cumsum()

        # Adding Installed Capacity to US (This is already 'Cumulative') so not including it in UScum
        # We are also renaming it to 'ActiveCapacity' and calculating Decommisioned Capacity.
        # TODO: Rename Installed_CApacity to ActiveCapacity throughout.
        keywd='Effective_Capacity_[W]'
        for scen in scenarios:
            USyearly['ActiveCapacity_'+self.name+'_'+scen+'_[MW]'] = self.scenario[scen].dataOut_m[keywd]/1e6 #this value is cumulative
            #decommissions are cumulative
            USyearly['DecommisionedCapacity_'+self.name+'_'+scen+'_[MW]'] = (UScum['newInstalledCapacity_'+self.name+'_'+scen+'_[MW]'] - USyearly['ActiveCapacity_'+self.name+'_'+scen+'_[MW]'])

        # Adding Decommissioned Capacity

        # Reindexing and Merging
        USyearly.index = self.scenario[scen].dataIn_m['year']
        UScum.index = self.scenario[scen].dataIn_m['year']

        self.USyearly = USyearly
        self.UScum = UScum

        return USyearly, UScum
    
    def aggregateEnergyResults(self, scenarios=None, materials=None):
        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        if materials is None:
            materials = list(self.scenario[scenarios[0]].material.keys())
        else:
            if isinstance(materials, str):
                materials = [materials]
        
        #TODO: categorize the energy in values into lifecycle stages
        mfg_energies = ['mod_MFG','mat_extraction','mat_MFG_virgin']
        mfg_recycle_energies_LQ = ['mat_MFGScrap_LQ'] #LQ and HQ are separate becuase LQ is only LQ
        mfg_recycle_energies_HQ = ['mat_MFGScrap_HQ'] #and HQ material is E_LQ + E_HQ
        use_energies = ['mod_Install','mod_OandM','mod_Repair']
        eol_energies = ['mat_Landfill','mod_Demount','mod_Store','mod_Resell_Certify']
        eol_remfg_energies = ['mod_ReMFG_Disassmbly','mat_EoL_ReMFG_clean']
        eol_recycle_energies_LQ = ['mod_Recycle_Crush','mat_Recycled_LQ']
        eol_recycle_energies_HQ = ['mod_Recycle_Crush','mat_Recycled_HQ']

        energy_demands_keys = [mfg_energies,mfg_recycle_energies_LQ,mfg_recycle_energies_HQ,use_energies,eol_energies,eol_remfg_energies,eol_recycle_energies_LQ,eol_recycle_energies_HQ]
        energy_demands_flat = list(itertools.chain(*energy_demands_keys))
        
        #init variables
        allenergy = pd.DataFrame()
        energyGen = pd.DataFrame()
        energyFuel = pd.DataFrame()
        energyDemands = pd.DataFrame()
        energyDemands_all = pd.DataFrame()

        for scen in scenarios:
            # add the scen name as a prefix \
            
            energy_mod_scen = self.scenario[scen].dataOut_e.add_prefix(str(scen+'_')) #extract and label de module (10cols)
            
            scenmatde = pd.DataFrame() #wipe and initialize material energy df
            
            #material level energy
            for mat in materials:
                # add the scen name as a prefix 
                energy_mat_scen = self.scenario[scen].material[mat].matdataOut_e.add_prefix(str(scen+'_'+mat+'_')) #extract and label de material
                scenmatde = pd.concat([scenmatde,energy_mat_scen], axis=1) #group all material de (84)
            
            scende = pd.concat([energy_mod_scen,scenmatde], axis=1) #group single scenario de (module and materials) (94cols)
            scende_gen = scende.filter(like='e_out_annual')# create df of energy generation
            scende_fuels = scende.filter(like='_fuel')# create df of fuel
            scende_filter1 = scende.loc[:,~scende.columns.isin(scende_gen.columns)] #select all columns that are NOT energy generation
            scende_demands = scende_filter1.loc[:,~scende_filter1.columns.isin(scende_fuels.columns)] #select all columns that are NOT fuel (this avoids double counting)
            colname = str(scen+'_e_demand_total') #create column name
            scende_demands.loc[:,colname] = scende_demands.sum(axis=1) #sums module and material energy demands
            
            allenergy = pd.concat([allenergy, scende], axis=1) #collect all scenarios de (excludes demand sum)
            energyDemands = pd.concat([energyDemands,scende_demands], axis=1) #collect energy demands (includes demand sum column)
            energyGen = pd.concat([energyGen, scende_gen], axis=1) #collect all scenarios energy generation
            energyFuel = pd.concat([energyFuel, scende_fuels], axis=1) #collect all scenarios fuel energy demands
            energyDemands_all = pd.concat([energyDemands_all, scende_demands, scende_fuels], axis=1)
        
        
        #Fix the index to be years
        allenergy.index = self.scenario[scen].dataIn_e['year']
        energyDemands_all.index = self.scenario[scen].dataIn_e['year']
        energyGen.index = self.scenario[scen].dataIn_e['year']

                
        return allenergy, energyGen, energyDemands_all #note, all these are annual
        

    def plotScenariosComparison(self, keyword=None, scenarios=None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        if keyword is None:
            # TODO: Not ideal way to provide this info, but will have to work for this release.
            scen = list(self.scenario.keys())[0]
            print("Please pass a keyword:")
            if hasattr(self.scenario[scen], 'dataIn_m'):
              print("\n ** Scenario Data In Mass ", list(self.scenario[scen].dataIn_m.keys()))
            if hasattr(self.scenario[scen], 'dataOut_m'):
              print("\n ** Scenario Data Out Mass ", list(self.scenario[scen].dataOut_m.keys()))
            if hasattr(self.scenario[scen], 'dataIn_e'):
              print("\n ** Scenario Data In Energy ", list(self.scenario[scen].dataIn_e.keys()))
            if hasattr(self.scenario[scen], 'dataOut_e'):
              print("\n ** Scenario Data Out Energy ", list(self.scenario[scen].dataOut_e.keys()))
                  
            return

        
        yunits = _unitReferences(keyword)

        plt.figure()

        
        for scen in scenarios:      
            if hasattr(self.scenario[scen], 'dataIn_e'):
                dataIn_e = True
            else:
                dataIn_e = False
                
            # Not very elegant but works?
            if keyword in self.scenario[scen].dataIn_m:                
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].dataIn_m[keyword], label=scen)
            elif keyword in self.scenario[scen].dataOut_m: 
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].dataOut_m[keyword], label=scen)
            elif dataIn_e:
                if keyword in self.scenario[scen].dataIn_e: 
                    plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].dataIn_e[keyword], label=scen) 
                # the year column is not getting added to the dataOut DFs   
                elif keyword in self.scenario[scen].dataOut_e: 
                    plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].dataOut_e[keyword], label=scen)
                else:
                    print("No data for ", keyword, "for Scenario ", scen)
            plt.legend()
        plt.xlabel('Year')
        plt.title(keyword.replace('_', " "))
        plt.ylabel(yunits)


    def plotMetricResults(self):
        from plotly.subplots import make_subplots
       # import plotly.graph_objects as go


        y1 = self.plotMaterialResults(keyword='VirginStock', yearlyorcumulative='yearly')
        y2 = self.plotMaterialResults(keyword='WasteAll', yearlyorcumulative='yearly')
        y3 = self.plotMaterialResults(keyword='WasteEOL', yearlyorcumulative='yearly')
        y4 = self.plotMaterialResults(keyword='WasteMFG', yearlyorcumulative='yearly')
        c1 = self.plotMaterialResults(keyword='VirginStock', yearlyorcumulative='cumulative')
        c2 = self.plotMaterialResults(keyword='WasteAll', yearlyorcumulative='cumulative')
        c3 = self.plotMaterialResults(keyword='WasteEOL', yearlyorcumulative='cumulative')
        c4 = self.plotMaterialResults(keyword='WasteMFG', yearlyorcumulative='cumulative')
        ic = self.plotInstalledCapacityResults()

    def plotMaterialResults(self, keyword, yearlyorcumulative='yearly', cumplot=False):
        import plotly.express as px
        import re

        if yearlyorcumulative == 'yearly':
            data = self.USyearly
        else:
            data = self.UScum

        if keyword is None:
            print("keyword options are :" 'VirginStock', 'WasteALL', 'WasteEOL', 'WasteMFG')
            return
            #TODO: add a split to first bracket and print unique values option and return.

        filter_col = [col for col in data if col.startswith(keyword)]

        # Getting Title, Y-Axis Labels, and Legend Readable
        titlekeyword = str.capitalize(yearlyorcumulative) + re.sub( r"([A-Z])", r" \1", keyword)
        units = filter_col[0].split('_')[-1]

        mylegend = [col.split('_')[1:] for col in filter_col]
        mylegend = [col[:-1] for col in mylegend]
        mylegend = [' '.join(col) for col in mylegend]
        mylegend = [str.capitalize(col) for col in mylegend]

        fig = px.line(data[filter_col], template="plotly_white")

        fig.update_layout(
            title=titlekeyword,
            xaxis_title="Year",
            yaxis_title=units
        )

        for idx, name in enumerate(mylegend):
            fig.data[idx].name = name
            fig.data[idx].hovertemplate = name

        if cumplot:
            return fig
        else:
            fig.show()
        return

    def plotInstalledCapacityResults(self, cumplot=False):
        # TODO: Add scenarios input to subselect which ones to plot.

        import plotly.express as px

        datay = self.USyearly
        datac = self.UScum

        filter_colc = [col for col in datac if col.startswith('newInstalledCapacity')]
        filter_coly = [col for col in datay if col.startswith('ActiveCapacity')]

        datay = datay[filter_coly].copy()
        mylegend = [col.split('_')[1:] for col in datay]
        mylegend = [col[:-1] for col in mylegend]
        mylegend = [str(col)[2:-2] for col in mylegend]
        mylegendy = ['Active Capacity, '+col for col in mylegend]

        print(mylegend)

        datac = datac[filter_colc].copy()
        mylegend = [col.split('_')[1:] for col in datac]
        mylegend = [col[:-1] for col in mylegend]
        mylegend = [str(col)[2:-2] for col in mylegend]
        mylegendc = ['Cumulative New Installs, '+col for col in mylegend]

        data = datay.join(datac)
        mylegend = mylegendy + mylegendc

        titlekeyword = 'Installed Capacity and Cumulative new Installs'


        # Getting Title, Y-Axis Labels, and Legend Readable
        units = filter_colc[0].split('_')[-1]



        fig = px.line(data, template="plotly_white")

        fig.update_layout(
            title=titlekeyword,
            xaxis_title="Year",
            yaxis_title=units
        )

        for idx, name in enumerate(mylegend):
            fig.data[idx].name = name
            fig.data[idx].hovertemplate = name

        if cumplot:
            return fig
        else:
            fig.show()
        return


    def plotMaterialComparisonAcrossScenarios(self, keyword=None, scenarios=None, material = None):

        if scenarios is None:
            scenarios = list(self.scenario.keys())
        else:
            if isinstance(scenarios, str):
                scenarios = [scenarios]

        if keyword is None:
            # TODO: Prettify this.
            try:
                scens = list(self.scenario.keys())[0]
                mats = list(self.scenario[scens].material.keys())[0]
                print("Choose one of the keywords: ",  
                "\n ** Material Data In Mass ", list(self.scenario[scens].material[mats].matdataIn_m.keys()),
                "\n ** Material Data In Energy ", list(self.scenario[scens].material[mats].matdataIn_e.keys()),
                "\n ** Material Data Out Mass ", list(self.scenario[scens].material[mats].matdataOut_m.keys()),
                "\n ** Material Data Out Energy ", list(self.scenario[scens].material[mats].matdataOut_e.keys())
                )
            except:
                print("Please pass a keyword.")             
            return

        if material is None:
            scens = list(self.scenario.keys())[0]
            mats = list(self.scenario[scens].material.keys())
            print("Choose one of the Materials: ", mats)
            return
        else:
            if isinstance(material, str) is False:
                mats = list(self.scenario[scens].material.keys())
                print("Can only pass one material name (str). Choose one of the Materials: ", mats)
                return

        yunits = _unitReferences(keyword)

        plt.figure()

        for scen in scenarios:
            if keyword in self.scenario[scen].material[material].matdataIn_m:                
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].material[material].matdataIn_m[keyword], label=scen)
            elif keyword in self.scenario[scen].material[material].matdataIn_e:   
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].material[material].matdataIn_e[keyword], label=scen)
            elif keyword in self.scenario[scen].material[material].matdataOut_m:   
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].material[material].matdataOut_m[keyword], label=scen)
            elif keyword in self.scenario[scen].material[material].matdataOut_e:   
                plt.plot(self.scenario[scen].dataIn_m['year'],self.scenario[scen].material[material].matdataOut_e[keyword], label=scen)
            else:
                print("No data for ", keyword, "for Scenario ", scen)
    
        plt.legend()
        plt.xlabel('Year')
        plt.title((material + ' ' + keyword.replace('_', " ")))
        plt.ylabel(yunits)


class Scenario(Simulation):

    def __init__(self, name, massmodulefile=None, energymodulefile = None, file=None):

        if massmodulefile is None and file is not None:
            print("Deprecation warning: file has been deprecated as of v 0.3 as",
                  "an input to class Scenario and will be fully removed for v 0.4;",
                  "Use 'massmodulefile' instead. \n Internally renaming as massmodulefile to continue")
            massmodulefile = file

        self.name = name
        self.material = {}

        if massmodulefile is None:
            try:
                massmodulefile = _interactive_load('Select module baseline (mass) file')
            except:
                raise Exception('Interactive load failed. Tkinter not supported'+
                                'on this system. Try installing X-Quartz and reloading')

        data, meta = _readPVICEFile(massmodulefile)

        self.baselinefile = file
        self.metdataIn_m = meta
        self.dataIn_m = data
        
        if energymodulefile is not None:
            self.addEnergytoModule(energymodulefile)

    def addEnergytoModule(self, energymodulefile):
        data, meta = _readPVICEFile(energymodulefile)

        self.energyfile = energymodulefile
        self.metdataIn_e = meta
        self.dataIn_e = data

    def addMaterial(self, materialname, massmatfile=None, energymatfile=None,
                    file=None):
        '''
        Adds a material object, assigning its name and loading mass and energy
        data.

        Inputs
        --------
        materialname : string
            String of the material to import, assigned to the material object.  
        massmatfile : file
            Path including filename to the material file to load
        energymatfile : str
            Path including filename to the material file to load

            
        '''

        if massmatfile is None and file is not None:
            print("Deprecation warning: file has been deprecated as of v 0.3 as",
                  "an input to class Material and will be fully removed for v 0.4;",
                  "Use 'massmatfile' instead. \n Internally renaming as massmatfile to continue")
            massmatfile = file

        self.material[materialname] = Material(materialname, massmatfile, energymatfile)
            


    def addMaterials(self, materials, baselinefolder=None, matnameformatMass=None,
                     matnameformatEnergy=None):
        '''
        Inputs
        --------
        materialname : list of strings(preferred)
            List of materials to loop over and add to the simulation.
            Single material string (i.e. 'glass') can be passed but converted to
            list. Examples: materials = ['glass', 'silver']  
        baselinefolder : path
            Path to where the material folders are stored
        matnameformatMass : str
            Format of the material baseline files mass names, including a bracket for 
            formatting in the materialname. i.e.
            'baseline_material_mass_{}.csv'
        matnameformatEnergy : str
            Format of the material baseline files energy names, including a bracket for 
            formatting in the materialname. i.e.
            'baseline_material_energy_{}.csv'
        matnameformatEnergy : str
        '''
        if baselinefolder is None:
            baselinefolder = DATA_PATH

        # Checking if string passed for a single material, converting it to list
        if type(materials) == str:
            materials = [materials]
    
        if matnameformatMass is None:
            matnameformatMass = r'baseline_material_mass_{}.csv'
        if matnameformatEnergy is None:
            matnameformatEnergy = r'baseline_material_energy_{}.csv'
        for mat in materials:
            massmatfile = os.path.join(baselinefolder, matnameformatMass.format(mat))
            energymatfile = os.path.join(baselinefolder, matnameformatEnergy.format(mat))
            if os.path.isfile(energymatfile):
                print("Adding Mass AND Energy files for: ", mat )
            else:
                energymatfile = None
                print("Adding Mass files for: ", mat )
                
            self.material[mat] = Material(mat, massmatfile = massmatfile, 
                                          energymatfile = energymatfile)


    def modifyMaterials(self, materials, stage, value, start_year=None):

        if start_year is None:
            start_year = int(datetime.datetime.now().year)

        if materials is None:
            materials = list(self.material.keys())
        else:
            if isinstance(materials, str):
                materials = [materials]

        selectyears = self.dataIn_m['year']>=start_year
        
        if isinstance(value, (pd.Series)):
            for mat in materials:
                timeshift = start_year - self.dataIn_m.iloc[0,0]
                self.material[mat].matdataIn_m.loc[timeshift:, stage] = value.values
            
        else:
            for mat in materials:
                self.material[mat].matdataIn_m.loc[selectyears, stage] = value


    def modifyMaterialEnergy(self, materials, stage, value, start_year=None):

        if start_year is None:
            start_year = int(datetime.datetime.now().year)

        if materials is None:
            materials = list(self.material.keys())
        else:
            if isinstance(materials, str):
                materials = [materials]

        selectyears = self.dataIn_e['year']>=start_year
        
        if isinstance(value, (pd.Series)):
            for mat in materials:
                timeshift = start_year - self.dataIn_e.iloc[0,0]
                self.material[mat].matdataIn_e.loc[timeshift:, stage] = value.values
            
        else:
            for mat in materials:
                self.material[mat].matdataIn_e.loc[selectyears, stage] = value

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key):
        return setattr(self, key)


class Material:

    def __init__(self, materialname, massmatfile, energymatfile=None):
        self.materialname = materialname

        if massmatfile is None:
            try:
                massmatfile = _interactive_load('Select material baseline ' +
                                                'file')
            except:
                raise Exception('Interactive load failed. Tkinter not ' +
                                'supported on this system. Try installing ' +
                                'X-Quartz and reloading')

        data, meta = _readPVICEFile(massmatfile)

        self.massmatfile = massmatfile
        self.matmetdataIn_m = meta
        self.matdataIn_m = data

        # SAVING A COPY TO RAW
        # Joining the metdata back in
        foometa = pd.DataFrame(meta, index=[0])
        foodata = pd.concat([foometa, data], axis=0)
        # Removing the path to just get the filename
        # TODO - find fancy python way, this will probably break on a mac
        try:
            foomassmatfile = massmatfile.split('\\')[-1]
            foodata.to_csv(os.path.join('raw', materialname + '_' +
                                        foomassmatfile))
        except:
            print("Can't save raw files on macs yet.")
        if energymatfile is not None:
            self.addEnergytoMaterial(energymatfile)
        else:
            self.energymatfile = None
            self.matmetdataIn_e = None
            self.matdataIn_e = None

    def addEnergytoMaterial(self, energymatfile):

        data, meta = _readPVICEFile(energymatfile)

        self.energymatfile = energymatfile
        self.matmetdataIn_e = meta
        self.matdataIn_e = data


def weibull_params(keypoints):
    r'''Returns shape parameter `alpha` and scale parameter `beta`
    for a Weibull distribution whose CDF passes through the
    two time: value pairs in `keypoints`

    Parameters
    ----------
    keypoints : list
        Two lists of t50 and 590 values, where t50 is the year since deployment
        that the cohort has lost 50% of originally installed modules, and t90
        is the year since deployment that the cohort has lost 90% of the originally
        installed modules. These values are used to calcualte the shape and scale
        parameters for the weibull distribution.

    Returns
    -------
    alpha : float
        Shape parameter `alpha` for weibull distribution.
    beta : float
        Scale parameter `beta` for weibull distribution. Often exchanged with ``lifetime``
        like in Irena 2016, beta = 30.

    '''

    t1, t2 = tuple(keypoints.keys())
    cdf1, cdf2 = tuple(keypoints.values())
    alpha = np.ndarray.item(np.real_if_close(
        (np.log(np.log(1 - cdf1)+0j) - np.log(np.log(1 - cdf2)+0j))/(np.log(t1) - np.log(t2))
    ))
    beta = np.abs(np.exp(
        (
            np.log(t2)*((0+1j)*np.pi + np.log(np.log(1 - cdf1)+0j))
            + np.log(t1)*(((0-1j))*np.pi - np.log(np.log(1 - cdf2)+0j))
        )/(
            np.log(np.log(1 - cdf1)+0j) - np.log(np.log(1 - cdf2)+0j)
        )
    ))
    return {'alpha': alpha, 'beta': beta}

def weibull_cdf(alpha, beta):
    '''Return the CDF for a Weibull distribution having:
    shape parameter `alpha`
    scale parameter `beta`

    Parameters
    ----------
    alpha : float
        Shape parameter `alpha` for weibull distribution.
    beta : float
        Scale parameter `beta` for weibull distribution. Often exchanged with ``lifetime``
        like in Irena 2016, beta = 30.

    '''

    def cdf(x):
        return 1 - np.exp(-(np.array(x)/beta)**alpha)
    return cdf

def weibull_pdf(alpha, beta):
    r'''Return the PDF for a Weibull distribution having:
        shape parameter `alpha`
        scale parameter `beta`

    Parameters
    ----------
    alpha : float
        Shape parameter `alpha` for weibull distribution.
    beta : float
        Scale parameter `beta` for weibull distribution. Often exchanged with ``lifetime``
        like in Irena 2016, beta = 30.

    '''

    def pdf(x):
        return (alpha/np.array(x)) * ((np.array(x)/beta)**alpha) * (np.exp(-(np.array(x)/beta)**alpha))

    return pdf

def weibull_pdf_vis(alpha, beta, xlim=56):
    r''' Returns the CDF for a weibull distribution of 1 generation
    so it can be plotted.

    Parameters
    ----------
    alpha : float
        Shape parameter `alpha` for weibull distribution.
    beta : float
        Scale parameter `beta` for weibull distribution. Often exchanged with ``lifetime``
        like in Irena 2016, beta = 30.
    xlim : int
        Number of years to calculate the distribution for. i.e. x-axis limit.

    Returns
    -------
    idf : list
        List of weibull cumulative distribution values for year 0 until xlim.

    '''

    dfindex = pd.RangeIndex(0,xlim,1)
    x = np.clip(dfindex - 0, 0, np.inf)

    if alpha and beta:
        i = weibull_pdf(alpha, beta)

    idf = list(map(i, x))

    return idf


def weibull_cdf_vis(alpha, beta, xlim=56):
    r''' Returns the CDF for a weibull distribution of 1 generation
    so it can be plotted.

    Parameters
    ----------
    alpha : float
        Shape parameter `alpha` for weibull distribution.
    beta : float
        Scale parameter `beta` for weibull distribution. Often exchanged with ``lifetime``
        like in Irena 2016, beta = 30.
    xlim : int
        Number of years to calculate the distribution for. i.e. x-axis limit.

    Returns
    -------
    idf : list
        List of weibull cumulative distribution values for year 0 until xlim.

    '''

    dfindex = pd.RangeIndex(0,xlim,1)
    x = np.clip(dfindex - 0, 0, np.inf)

    if alpha and beta:
        i = weibull_cdf(alpha, beta)

    idf = list(map(i, x))

    return idf


def sens_StageImprovement(df, stage, improvement=1.3, start_year=None):
    '''
    Modifies baseline scenario for evaluating sensitivity of lifetime parameter.
    t50 and t90 reliability years get incresed by `improvement` parameter
    starting the `year_increase` year specified.

    Parameters
    ----------
    df : dataframe
        dataframe to be modified
    stage : str
        Stage that wants to be modified. This can be any of the module or
        material specified values, for example:'MFG_Material_eff',
        'mat_MFG_scrap_recycled', 'mat_MFG_scrap_Recycled',
        'mat_MFG_scrap_Recycled_into_HQ', 'mat_MFG_scrap_Recycled_into_HQ_Reused4MFG'
        'mod_EOL_collection_losses', 'mod_EOL_collected_recycled',
        'mat_EOL_Recycling_yield', 'mat_EOL_Recycled_into_HQ',
        'mat_EOL_RecycledHQ_Reused4MFG', 'mod_Repair',
        'mod_MerchantTail', 'mod_Reuse', 'mod_eff', etc.
    improvement : decimal
        Percent increase in decimal (i.e. "1.3" for 30% increase in value)
        or percent decrease (i.e. "0.3") relative to values in df.
    start_year :
        the year at which the improvement occurs

    Returns
    --------
    df : dataframe
        dataframe of expected module lifetime increased or decreased at specified year
    '''


    if start_year is None:
        start_year = int(datetime.datetime.now().year)

    #df[df.index > 2000]['mod_reliability_t50'].apply(lambda x: x*1.3)
    df[stage] = df[stage].astype(float)
    df.loc[df.index > start_year, stage] = df[df.index > start_year][stage].apply(lambda x: x*improvement)

    return df


def sens_StageEfficiency(df, stage, target_eff = 95.0, start_year = None,
                         goal_year = 2030, plotflag = False):
    '''
    Modifies baseline scenario for evaluating sensitivity to increasing a stage in the
    lifetime of the module's efficiency. It either increases or decreases from the
    start year until the goal year the value to the target efficiency by interpolation.

    Parameters
    ----------
    df : dataframe
        dataframe to be modified
    stage : str
        Stage that wants to be modified. This can be any of the module or
        material specified efficiencies, for example:'MFG_Material_eff',
        'mat_MFG_scrap_recycled', 'mat_MFG_scrap_Recycled',
        'mat_MFG_scrap_Recycled_into_HQ', 'mat_MFG_scrap_Recycled_into_HQ_Reused4MFG'
        'mod_EOL_collection_losses', 'mod_EOL_collected_recycled',
        'mat_EOL_Recycling_yield', 'mat_EOL_Recycled_into_HQ',
        'mat_EOL_RecycledHQ_Reused4MFG', 'mod_Repair',
        'mod_MerchantTail', 'mod_Reuse', 'mod_eff', etc.
    start_year: int
        Year to start modifying the value. This specifies the initial efficiency
        value that is going to be modified. If None is passed, current year is used.
    target_eff: flat
        target eff value in percentage to be reached. i.e. 95.0 %.
    goal_year : int
        year by which target efficiency will be reached. i.e. 2030. Must be higher than current year.

    Returns
    -------
    df : dataframe
        modified dataframe
    '''

    if start_year is None:
        start_year = int(datetime.datetime.now().year)

    if start_year > goal_year:
        print("Error. Goal Year is before start year")
        return

    if 0 < abs(target_eff) < 1:  # checking it is not 0.95 but 95% i.e.
        print("Warning: target_eff value is between 0 and 1; it has been"
              "multiplied by 100% assuming it was a percentage in decimal form.")
        target_eff = target_eff*100

    if target_eff > 100 or target_eff < 0:
        print("Warning: target_eff is out of range. Input value between"
              "0 and 100")
        return

    if stage in df.columns:
        df2 = df.copy()
        df2[stage]=df2[stage].astype(float)
        df2.loc[(df2.index < goal_year) & (df2.index > start_year), stage] = np.nan
        df2.loc[df2.index >= goal_year , stage] = target_eff
        df2[stage] = df2[stage].interpolate()

        if plotflag:
            plt.plot(df[stage], label='Original')
            plt.plot(df2[stage], label='Modified')
            plt.title('Updated values for '+stage)
            plt.legend()
        return df2
    else:
        print("Stage name incorrect.")






def _modDict(originaldict, moddict):
    '''
    Compares keys in originaldict with moddict and updates values of
    originaldict to moddict if existing.

    Parameters
    ----------
    originaldict : dictionary
        Original dictionary calculated, for example frontscan or backscan dictionaries.
    moddict : dictionary
        Modified dictinoary, for example modscan['x'] = 0 to change position of x.

    Returns
    -------
    originaldict : dictionary
        Updated original dictionary with values from moddict.
    '''
    for key in moddict:
        try:
            originaldict[key] = moddict[key]
        except:
            print("Wrong key in modified dictionary")

    return originaldict


def calculateLCA(PVarea, modified_impacts=None, printflag = False):
    '''


    '''

    if printflag:
        print("Doing calculations of LCA analysis for Silicon Photovoltaic Panels")



    impacts = {'Acidification':{'UUID':  '75d0c8a2-e466-3bd7-813b-5beef2209330',
                                'Result':  1.29374135667815,
                                'Unit': 'g SO2' },
                'Carcinogenics':{'UUID':  'a6e5e5d8-a1e5-3c77-8170-586c4fe37514',
                                            'Result':  0.0000231966690476102,
                                            'Unit': 'CTUh' },
                'Ecotoxicity':{'UUID': '338e9370-ceb0-3d18-9d87-5f91feb7829c',
                                            'Result':  5933.77859696668,
                                            'Unit': 'CTUe' },
                'Eutrophication':{'UUID':  '45b8cd56-498a-3c6f-9488-134e951d8c02',
                                'Result':  1.34026194777363,
                                'Unit': 'kg N eq' },

                'Fossil fuel depletion':{'UUID': '0e45786f-67fa-3b8a-b8a3-73a7c316434c',
                                'Result': 249.642261689385,
                                'Unit': 'MJ surplus' },

                'Global warming':{'UUID':  '31967441-d687-313d-9910-13da3a584ab7',
                                'Result': 268.548841324818,
                                'Unit': 'kg CO2 eq' },

                'Non carcinogenics':{'UUID':  'd4827ae3-c873-3ea4-85fb-860b7f3f2dee',
                                'Result': 0.000135331806321799,
                                'Unit': 'CTUh' },

                'Ozone depletion':{'UUID': '6c05dad1-6661-35f2-82aa-6e8e6a498aec',
                                'Result':  0.0000310937628622019,
                                'Unit': 'kg CFC-11 eq' },

                'Respiratory effects':{'UUID':  'e0916d62-7fbd-3d0a-a4a5-52659b0ac9c1',
                                'Result':  0.373415542664206,
                                'Unit': 'kg PM2.5 eq' },
                'Smog':{'UUID':  '7a149078-e2fd-3e07-a5a3-79035c60e7c3',
                                'Result':  15.35483065,
                                'Unit': 'kg O3 eq' },
            }

    if modified_impacts is not None:
        impacts = _modDict(impacts, modified_impacts)
        if printflag:
            print("Following Modified impacts provided instead of TRACI 2.1 default")
            print(impacts)
            print("")
    else:
        if printflag:
            print("Following TRACI 2.1")

    acidification = impacts['Acidification']['Result']*PVarea
    carcinogenics = impacts['Carcinogenics']['Result']*PVarea
    ecotoxicity  = impacts['Ecotoxicity']['Result']*PVarea
    eutrophication = impacts['Eutrophication']['Result']*PVarea
    fossil_fuel_depletion = impacts['Fossil fuel depletion']['Result']*PVarea
    global_warming = impacts['Global warming']['Result']*PVarea
    non_carcinogenics = impacts['Non carcinogenics']['Result']*PVarea
    ozone_depletion = impacts['Ozone depletion']['Result']*PVarea
    respiratory_effects = impacts['Respiratory effects']['Result']*PVarea
    smog = impacts['Smog']['Result']*PVarea



    if printflag:
        print("RESULTS FOR PV AREA ", PVarea, " m2 ")
        print("****************************************")
        print('Acidification: ', round(impacts['Acidification']['Result']*PVarea, 2), ' ', impacts['Acidification']['Unit'])
        print('Carcinogenics: ', round(impacts['Carcinogenics']['Result']*PVarea, 2), ' ', impacts['Carcinogenics']['Unit'])
        print('Ecotoxicity: ', round(impacts['Ecotoxicity']['Result']*PVarea, 2), ' ', impacts['Ecotoxicity']['Unit'])
        print('Eutrophication: ', round(impacts['Eutrophication']['Result']*PVarea, 2), ' ', impacts['Eutrophication']['Unit'])
        print('Fossil fuel depletion: ', round(impacts['Fossil fuel depletion']['Result']*PVarea, 2), ' ', impacts['Fossil fuel depletion']['Unit'])
        print('Global warming: ', round(impacts['Global warming']['Result']*PVarea, 2), ' ', impacts['Global warming']['Unit'])
        print('Non carcinogenics: ', round(impacts['Non carcinogenics']['Result']*PVarea, 2), ' ', impacts['Non carcinogenics']['Unit'])
        print('Ozone depletion: ', round(impacts['Ozone depletion']['Result']*PVarea, 2), ' ', impacts['Ozone depletion']['Unit'])
        print('Respiratory effects: ', round(impacts['Respiratory effects']['Result']*PVarea, 2), ' ', impacts['Respiratory effects']['Unit'])
        print('Smog: ', round(impacts['Smog']['Result']*PVarea, 2), ' ', impacts['Smog']['Unit'])

    return (acidification, carcinogenics, ecotoxicity, eutrophication,
                fossil_fuel_depletion, global_warming,
                non_carcinogenics, ozone_depletion, respiratory_effects, smog)
