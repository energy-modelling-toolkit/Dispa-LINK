import sys, os

sys.path.append(os.path.abspath(r'..'))

# Simulation related
date_str = '1/1/2015'
hourly_periods = 8760

input_folder_fromPrepare = '../Inputs/EnergyScope/'
output_folder_fromPrepare = '../Outputs/EnergyScope/'
input_PP_folder_fromPrepare = '../Dispa-SET.git/Database/PowerPlants/'

input_folder = '../' + input_folder_fromPrepare
# output_folder = '../' + output_folder_fromPrepare
output_folder = output_folder_fromPrepare
input_PP_folder = '../' + input_PP_folder_fromPrepare  # input file = PowerPlants.csv

# Define constants
n_TD = 12  # Enter the number of TD specified in EnergyScope
countries = list(['BE'])  # ,'CH','FR'])                   #Enter countries studied
# perc_dhn_list = list([0.02])#, 0.37, 0.37])              #Percentage of LT Heat provided by DHN in EnergyScope
DHN_Prod_losses_list = list([0.05])  # , 0.05, 0.05])      #Percentage of DHN LT heat production losses in EnergyScope
DHN_Sto_losses_list = list([0.0000606])  # , 0.0000606, 0.0000606])
grid_losses_list = list([0.047])  # , 0.047, 0.047])       #Percentage of elec grid losses in EnergyScope

# List of ES output files
ES_txtfiles = ['Assets', 'Distri_E_stored', 'ElecLayers', 'H2Layers', 'HTLayers', 'YearBalance', 'cost_breakdown',
               'Distri_TS', 'FREIGHTLayers', 'gwp_breakdown', 'losses', 'PASSANGERSLayers']

# Lists of tech
elec_mobi_tech = ['TRAMWAY_TROLLEY', 'TRAIN_PUB', 'TRAIN_FREIGHT']  # electro mobility technology
ccs_tech = ['ATM_CCS', 'INDUSTRY_CCS']
hvc_tech = ['BIOMASS_TO_HVC', 'GAS_TO_HVC', 'OIL_TO_HVC']
p2h_tech = ['IND_DIRECT_ELEC', 'DHN_HP_ELEC', 'DEC_HP_ELEC', 'DEC_DIRECT_ELEC']
chp_tech = ['IND_COGEN_GAS', 'IND_COGEN_WOOD', 'IND_COGEN_WASTE', 'DHN_COGEN_GAS', 'DHN_COGEN_WOOD', 'DHN_COGEN_WASTE',
            'DEC_COGEN_GAS', 'DEC_COGEN_OIL', 'DHN_COGEN_WET_BIOMASS', 'DEC_COGEN_GAS']
OtherHeat_tech = ['IND_BOILER_GAS', 'IND_BOILER_WASTE', 'IND_BOILER_COAL', 'IND_BOILER_WOOD', 'IND_BOILER_OIL',
                  'DHN_DEEP_GEO', 'DHN_BOILER_GAS', 'DHN_BOILER_OIL', 'DEC_BOILER_GAS', 'DEC_BOILER_WOOD',
                  'DEC_BOILER_OIL', 'DEC_SOLAR', 'DEC_THHP_GAS']
power_tech = ['CCGT', 'PV', 'WIND_ONSHORE', 'WIND_OFFSHORE', 'WIND', 'IND_COGEN_GAS', 'IND_COGEN_WASTE',
              'DHN_COGEN_GAS', 'DHN_COGEN_WOOD', 'DHN_COGEN_WET_BIOMASS', 'DHN_COGEN_WASTE', 'HYDRO_RIVER', 'NUCLEAR',
              'GEOTHERMAL', 'COAL_US', 'DEC_COGEN_GAS']
storage_tech = ['PHS', 'BATT_LI', 'TS_DHN_SEASONAL', 'PHES', 'DAM_STORAGE']
OtherMob_tech = ['CAR_HEV', 'BUS_COACH_HYDIESEL', 'BOAT_FREIGHT_NG', 'TRUCK_NG', 'CAR_FUEL_CELL']
H2_tech_elec = ['H2_ELECTROLYSIS']
H2_tech = ['H2_NG', 'H2_ELECTROLYSIS']
capa_margin_tech = ['CCGT', 'PHS', 'COAL_US']  # 'BATT_LI','GEOTHERMAL'
dhn_tech = ['DHN_HP_ELEC', 'DHN_COGEN_GAS', 'DHN_COGEN_WOOD', 'DHN_COGEN_WET_BIOMASS', 'DHN_COGEN_WASTE',
            'DHN_BOILER_GAS', 'DHN_BOILER_OIL', 'DHN_DEEP_GEO', 'DHN_SOLAR']

heat_demands = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']

dhn_heat_tech = ['DHN_HP_ELEC', 'DHN_COGEN_GAS', 'DHN_COGEN_WOOD', 'DHN_COGEN_WET_BIOMASS', 'DHN_COGEN_WASTE',
                 'DHN_BOILER_GAS', 'DHN_BOILER_OIL', 'DHN_DEEP_GEO', 'DHN_SOLAR',
                 'TS_DHN_DAILY_Pin', 'TS_DHN_DAILY_Pout',
                 'TS_DHN_SEASONAL_Pin', 'TS_DHN_SEASONAL_Pout']
decen_heat_tech = ['DEC_HP_ELEC', 'DEC_DIRECT_ELEC', 'DEC_COGEN_GAS', 'DEC_COGEN_OIL', 'DEC_COGEN_GAS',
                   'DEC_BOILER_GAS',
                   'DEC_BOILER_WOOD', 'DEC_BOILER_OIL', 'DEC_SOLAR', 'DEC_THHP_GAS',
                   'TS_DEC_DIRECT_ELEC_Pin', 'TS_DEC_DIRECT_ELEC_Pout',
                   'TS_DEC_HP_ELEC_Pin', 'TS_DEC_HP_ELEC_Pout',
                   'TS_DEC_THHP_GAS_Pin', 'TS_DEC_THHP_GAS_Pout',
                   'TS_DEC_COGEN_GAS_Pin', 'TS_DEC_COGEN_GAS_Pout',
                   'TS_DEC_COGEN_OIL_Pin', 'TS_DEC_COGEN_OIL_Pout',
                   'TS_DEC_ADVCOGEN_GAS_Pin', 'TS_DEC_ADVCOGEN_GAS_Pout',
                   'TS_DEC_ADVCOGEN_H2_Pin', 'TS_DEC_ADVCOGEN_H2_Pout',
                   'TS_DEC_BOILER_GAS_Pin', 'TS_DEC_BOILER_GAS_Pout',
                   'TS_DEC_BOILER_WOOD_Pin', 'TS_DEC_BOILER_WOOD_Pout',
                   'TS_DEC_BOILER_OIL_Pin', 'TS_DEC_BOILER_OIL_Pout']
ind_heat_tech = ['IND_DIRECT_ELEC', 'IND_COGEN_GAS', 'IND_COGEN_WOOD', 'IND_COGEN_WASTE', 'IND_BOILER_GAS',
                 'IND_BOILER_WASTE', 'IND_BOILER_COAL', 'IND_BOILER_WOOD', 'IND_BOILER_OIL', 'TS_HIGH_TEMP_Pin',
                 'TS_HIGH_TEMP_Pout']

common = {}
common['ES'] = {}
common['ES']['h2_fix_dem'] = ['BUS_COACH_FC_HYBRIDH2', 'CAR_FUEL_CELL', 'TRUCK_FUEL_CELL', 'HABER_BOSCH',
                              'SYN_METHANOLATION', 'SYN_METHANATION', 'END_USE']
common['ES']['h2_var_dem'] = []
common['ES']['h2_fix_sup'] = ['SMR', 'H2_BIOMASS', 'AMMONIA_TO_H2']
common['ES']['h2_var_sup'] = ['H2', 'H2_RE']
common['ES']['ammonia_fix_dem'] = ['AMMONIA_TO_H2', 'END_USE']
common['ES']['ammonia_var_dem'] = []
common['ES']['ammonia_fix_sup'] = ['HABER_BOSCH']
common['ES']['ammonia_var_sup'] = ['AMMONIA', 'AMMONIA_RE']
common['ES']['gas_fix_dem'] = ['BUS_COACH_CNG_STOICH', 'CAR_NG', 'BOAT_FREIGHT_NG', 'TRUCK_NG', 'GAS_TO_HVC', 'SMR', 'END_USE']
common['ES']['gas_var_dem'] = ['METHANE_TO_METHANOL']
common['ES']['gas_fix_sup'] = ['GASIFICATION_SNG', 'SYN_METHANATION', 'BIO_HYDROLYSIS']
common['ES']['gas_var_sup'] = ['GAS', 'GAS_RE', 'BIOMETHANATION']
common['ES']['ind_fix_dem'] = ['OIL_TO_HVC', 'BIOMASS_TO_HVC', 'AMMONIA_TO_H2', 'END_USE']
common['ES']['ind_var_dem'] = ['METHANOL_TO_HVC']
common['ES']['ind_fix_sup'] = ['IND_BOILER_WOOD', 'IND_BOILER_OIL', 'IND_BOILER_COAL', 'IND_BOILER_WASTE']
common['ES']['ind_var_sup'] = ['IND_BOILER_GAS']
common['ES']['dhn_fix_dem'] = ['END_USE']
common['ES']['dhn_var_dem'] = []
common['ES']['dhn_fix_sup'] = ['HABER_BOSCH', 'BIOMASS_TO_METHANOL', 'GASIFICATION_SNG', 'AMMONIA_TO_H2',
                               'SYN_METHANOLATION', 'SYN_METHANATION', 'DHN_BOILER_WOOD', 'DHN_BOILER_OIL', 'DHN_SOLAR']
common['ES']['dhn_var_sup'] = ['DHN_BOILER_GAS']
common['ES']['dec_fix_dem'] = ['END_USE']
common['ES']['dec_var_dem'] = []
common['ES']['dec_fix_sup'] = ['DEC_BOILER_WOOD', 'DEC_BOILER_OIL', 'DEC_SOLAR']
common['ES']['dec_var_sup'] = ['DEC_THHP_GAS', 'DEC_BOILER_GAS']
common['ES']['wood_fix_dem'] = ['END_USE', 'BIOMASS_TO_METHANOL', 'BIOMASS_TO_HVC', 'H2_BIOMASS', 'GASIFICATION_SNG',
                                'PYROLYSIS_TO_LFO', 'PYROLYSIS_TO_FUELS', 'IND_BOILER_WOOD', 'DHN_BOILER_WOOD',
                                'DEC_BOILER_WOOD']
common['ES']['wood_var_dem'] = []
common['ES']['wood_fix_sup'] = []
common['ES']['wood_var_sup'] = ['WOOD']
common['ES']['lfo_fix_dem'] = ['END_USE', 'OIL_TO_HVC', 'IND_BOILER_OIL', 'DHN_BOILER_OIL', 'DEC_BOILER_OIL']
common['ES']['lfo_var_dem'] = []
common['ES']['lfo_fix_sup'] = ['PYROLYSIS_TO_LFO']
common['ES']['lfo_var_sup'] = ['LFO']
common['ES']['coal_fix_dem'] = ['END_USE', 'IND_BOILER_COAL']
common['ES']['coal_var_dem'] = []
common['ES']['coal_fix_sup'] = []
common['ES']['coal_var_sup'] = ['COAL']
common['ES']['waste_fix_dem'] = ['END_USE', 'IND_BOILER_WASTE']
common['ES']['waste_var_dem'] = []
common['ES']['waste_fix_sup'] = []
common['ES']['waste_var_sup'] = ['WASTE']

# Lists for AvailibilityFactors
AvailFactors = ['PHOT', 'WTON', 'WTOF', 'HROR']  # Dispa-SET nomenclature
AvailFactors2 = ['PV', 'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_RIVER']  # EnergyScope Nomenclature
Inflows = ['HDAM', 'HPHS']
ReservoirLevels = ['HPHS']

# ---------------------------------------- DICO ----------------------------------------#
# For the moment, the dico is in the file, but this will have to be read from a .txt file
mapping = {}
mapping['ES'] = {}

# This dictionary is used to sort out wether a TECH is a PowerPlant, a CHP or a STO
mapping['ES']['SORT'] = {u'CCGT': u'ELEC',
                   u'CCGT_AMMONIA': u'ELEC',
                   u'COAL_US': u'ELEC',
                   u'COAL_IGCC': u'ELEC',
                   u'PV': u'ELEC',
                   u'GEOTHERMAL': u'ELEC',
                   u'NUCLEAR': u'ELEC',
                   u'HYDRO_RIVER': u'ELEC',
                   u'NEW_HYDRO_RIVER': u'ELEC',
                   u'WIND': u'ELEC',  # IF WIND is not specified, WIND is asumed to be ONSHORE
                   u'WIND_OFFSHORE': u'ELEC',
                   u'WIND_ONSHORE': u'ELEC',
                   u'IND_COGEN_GAS': u'CHP',  # ADD extraction/back-pressure/other
                   u'IND_COGEN_WOOD': u'CHP',  # ADD extraction/back-pressure/other
                   u'IND_COGEN_WASTE': u'CHP',  # ADD extraction/back-pressure/other
                   u'IND_BOILER_GAS': u'',
                   u'IND_BOILER_WOOD': u'',
                   u'IND_BOILER_OIL': u'',
                   u'IND_BOILER_COAL': u'',
                   u'IND_BOILER_WASTE': u'',
                   u'IND_DIRECT_ELEC': u'P2HT',  # P2HT ?
                   u'DHN_HP_ELEC': u'P2HT',  # P2HT ?
                   u'DHN_COGEN_GAS': u'CHP',  # ADD extraction/back-pressure/other
                   u'DHN_COGEN_WOOD': u'CHP',  # ADD extraction/back-pressure/other
                   u'DHN_COGEN_WASTE': u'CHP',  # ADD extraction/back-pressure/other
                   u'DHN_COGEN_WET_BIOMASS': u'CHP',  # ADD extraction/back-pressure/other
                   u'DHN_BOILER_GAS': u'',
                   u'DHN_BOILER_WOOD': u'',
                   u'DHN_BOILER_OIL': u'',
                   u'DHN_DEEP_GEO': u'',
                   u'DHN_SOLAR': u'',
                   u'DEC_HP_ELEC': u'P2HT',  # P2HT ?
                   u'DEC_THHP_GAS': u'HEAT',
                   u'DEC_COGEN_GAS': u'CHP',  # ADD extraction/back-pressure/other
                   u'DEC_COGEN_OIL': u'CHP',  # ADD extraction/back-pressure/other
                   u'DEC_ADVCOGEN_GAS': u'CHP',  # ADD extraction/back-pressure/other
                   u'DEC_ADVCOGEN_H2': u'CHP',  # ADD extraction/back-pressure/other
                   u'DEC_BOILER_GAS': u'',
                   u'DEC_BOILER_WOOD': u'',
                   u'DEC_BOILER_OIL': u'',
                   u'DEC_SOLAR': u'',
                   u'DEC_DIRECT_ELEC': u'P2HT',
                   u'PHS': u'STO',
                   u'PHES': u'STO',  # Same thing than PHS ?
                   u'DAM_STORAGE': u'STO',
                   u'BATT_LI': u'STO',
                   u'BEV_BATT': u'STO',
                   u'PHEV_BATT': u'STO',
                   u'TS_DEC_DIRECT_ELEC': u'STO',
                   u'TS_DEC_HP_ELEC': u'STO',  # P2HT ?
                   u'TS_DEC_THHP_GAS': u'STO',
                   u'TS_DEC_COGEN_GAS': u'STO',
                   u'TS_DEC_COGEN_OIL': u'STO',
                   u'TS_DEC_ADVCOGEN_GAS': u'STO',
                   u'TS_DEC_ADVCOGEN_H2': u'STO',
                   u'TS_DEC_BOILER_GAS': u'STO',
                   u'TS_DEC_BOILER_WOOD': u'STO',
                   u'TS_DEC_BOILER_OIL': u'STO',
                   u'TS_DHN_DAILY': u'STO',  # TO DO
                   u'TS_DHN_SEASONAL': u'STO',
                   u'TS_HIGH_TEMP': u'STO',# TO DO
                   u'SEASONAL_NG': u'',  # TO DO
                   u'SEASONAL_H2': u'P2GS_STO',
                   u'H2_STORAGE': u'P2GS_STO',
                   u'H2_ELECTROLYSIS': u'P2GS',
                   u'HABER_BOSCH': u'OTH'}  # TO DO

mapping['ES']['TECH'] = {u'CCGT': u'COMC',
                   u'CCGT_AMMONIA': u'COMCX',
                   u'COAL_US': u'STURX',
                   u'COAL_IGCC': u'STURX',
                   u'PV': u'PHOT',
                   u'GEOTHERMAL': u'STUR',
                   u'NUCLEAR': u'STUR',
                   u'HYDRO_RIVER': u'HROR',
                   u'Hydro_river': u'HROR',
                   u'NEW_HYDRO_RIVER': u'HROR',
                   u'WIND': u'WTON',
                   u'Wind_onshore': u'WTON',
                   u'Wind_offshore': u'WTOF',
                   # HYPOTHESIS : if not specified, Wind is assumed to be ONSHORE - TO CHECK
                   u'WIND_OCapitalfCapitalfSHORE': u'WTOF',
                   u'WIND_OFFSHORE': u'WTOF',
                   u'WIND_ONSHORE': u'WTON',
                   u'IND_COGEN_GAS': u'STUR',
                   u'IND_COGEN_WOOD': u'STURX',
                   u'IND_COGEN_WASTE': u'STURX',
                   u'IND_BOILER_GAS': u'',
                   u'IND_BOILER_WOOD': u'',
                   u'IND_BOILER_OIL': u'',
                   u'IND_BOILER_COAL': u'',
                   u'IND_BOILER_WASTE': u'',
                   u'IND_DIRECT_ELEC': u'REHE',  # TO CHECK
                   u'DHN_HP_ELEC': u'HYHP',  # TO CHECK : HP = Heat Pump ?
                   u'DHN_COGEN_GAS': u'COMC',
                   u'DHN_COGEN_WOOD': u'COMCX',
                   u'DHN_COGEN_WASTE': u'STURX',
                   u'DHN_COGEN_WET_BIOMASS': u'COMC',
                   u'DHN_BOILER_GAS': u'',
                   u'DHN_BOILER_WOOD': u'',
                   u'DHN_BOILER_OIL': u'',
                   u'DHN_DEEP_GEO': u'',
                   u'DHN_SOLAR': u'',
                   u'DEC_HP_ELEC': u'ASHP',  # TO CHECK : HP = Heat Pump ?
                   u'DEC_THHP_GAS': u'ABHP',
                   u'DEC_COGEN_GAS': u'GTUR',
                   u'DEC_COGEN_OIL': u'GTURX',
                   u'DEC_ADVCOGEN_GAS': u'COMC',
                   u'DEC_ADVCOGEN_H2': u'SOFC',
                   u'DEC_BOILER_GAS': u'',
                   u'DEC_BOILER_WOOD': u'',
                   u'DEC_BOILER_OIL': u'',
                   u'DEC_SOLAR': u'',
                   u'DEC_DIRECT_ELEC': u'REHE',  # TO CHECK : HP = Heat Pump ?
                   u'PHS': u'HPHS',
                   u'PHES': u'HPHS',
                   u'DAM_STORAGE': u'HDAM',
                   u'HYDRO_DAM': u'HDAM',
                   u'Hydro_dam': u'HDAM',
                   u'BATT_LI': u'BATS',
                   u'BEV_BATT': u'BEVS',
                   u'PHEV_BATT': u'BEVS',
                   u'TS_DEC_DIRECT_ELEC': u'THMS',
                   u'TS_DEC_HP_ELEC': u'THMS',
                   u'TS_DEC_THHP_GAS': u'THMS',
                   u'TS_DEC_COGEN_GAS': u'THMS',
                   u'TS_DEC_COGEN_OIL': u'THMS',
                   u'TS_DEC_ADVCOGEN_GAS': u'THMS',
                   u'TS_DEC_ADVCOGEN_H2': u'THMS',
                   u'TS_DEC_BOILER_GAS': u'THMS',
                   u'TS_DEC_BOILER_WOOD': u'THMS',
                   u'TS_DEC_BOILER_OIL': u'THMS',
                   u'TS_DHN_DAILY': u'THMS',  # TO DO
                   u'TS_DHN_SEASONAL': u'',
                   u'TS_HIGH_TEMP': u'',# TO DO
                   u'SEASONAL_NG': u'',  # TO DO
                   u'SEASONAL_H2': u'',
                   u'H2_STORAGE': u'',
                   u'H2_ELECTROLYSIS': u'P2GS',
                   u'HABER_BOSCH': u''}

mapping['ES']['FUEL'] = {u'CCGT': u'GAS',
                   u'CCGT_AMMONIA': u'AMO',
                   u'COAL_IGCC': u'HRD',
                   u'COAL_US': u'HRD',
                   u'PV': u'SUN',
                   u'GEOTHERMAL': u'GEO',
                   u'NUCLEAR': u'NUC',
                   u'HYDRO_RIVER': u'WAT',
                   u'NEW_HYDRO_RIVER': u'WAT',
                   u'WIND': u'WIN',  # IF WIND is not specified, WIND is asumed to be ONSHORE
                   u'WIND_OCapitalfCapitalfSHORE': u'WIN',
                   u'WIND_OFFSHORE': u'WIN',
                   u'WIND_ONSHORE': u'WIN',
                   u'IND_COGEN_GAS': u'GAS',
                   u'IND_COGEN_WOOD': u'BIO',
                   u'IND_COGEN_WASTE': u'WST',
                   u'IND_BOILER_GAS': u'GAS',
                   u'IND_BOILER_WOOD': u'BIO',
                   u'IND_BOILER_OIL': u'OIL',
                   u'IND_BOILER_COAL': u'HRD',
                   u'IND_BOILER_WASTE': u'WST',
                   u'IND_DIRECT_ELEC': u'ELE',  # P2HT ?
                   u'DHN_HP_ELEC': u'ELE',  # P2HT ?
                   u'DHN_COGEN_GAS': u'GAS',
                   u'DHN_COGEN_WOOD': u'BIO',
                   u'DHN_COGEN_WASTE': u'WST',
                   u'DHN_COGEN_WET_BIOMASS': u'BIO',
                   u'DHN_BOILER_GAS': u'GAS',
                   u'DHN_BOILER_WOOD': u'BIO',
                   u'DHN_BOILER_OIL': u'OIL',
                   u'DHN_DEEP_GEO': u'GEO',
                   u'DHN_SOLAR': u'SUN',
                   u'DEC_HP_ELEC': u'AIR',  # P2HT ?
                   u'DEC_THHP_GAS': u'GAS',
                   u'DEC_COGEN_GAS': u'GAS',
                   u'DEC_COGEN_OIL': u'OIL',
                   u'DEC_ADVCOGEN_GAS': u'GAS',
                   u'DEC_ADVCOGEN_H2': u'HYD',
                   u'DEC_BOILER_GAS': u'GAS',
                   u'DEC_BOILER_WOOD': u'BIO',
                   u'DEC_BOILER_OIL': u'OIL',
                   u'DEC_SOLAR': u'SUN',
                   u'DEC_DIRECT_ELEC': u'ELE',
                   u'PHS': u'WAT',
                   u'PHES': u'WAT',
                   u'DAM_STORAGE': u'WAT',
                   u'BATT_LI': u'OTH',  # Right fuel in DS terminology ??
                   u'BEV_BATT': u'OTH',  # Right fuel in DS terminology ??
                   u'PHEV_BATT': u'OTH',  # Right fuel in DS terminology ??
                   u'TS_DEC_DIRECT_ELEC': u'THE',  # P2HT ?  #Do I need to specify a fuel for Thermal Storage ?
                   u'TS_DEC_HP_ELEC': u'THE',  # P2HT ?
                   u'TS_DEC_THHP_GAS': u'THE',
                   u'TS_DEC_COGEN_GAS': u'THE',
                   u'TS_DEC_COGEN_OIL': u'THE',
                   u'TS_DEC_ADVCOGEN_GAS': u'THE',
                   u'TS_DEC_ADVCOGEN_H2': u'THE',
                   u'TS_DEC_BOILER_GAS': u'THE',
                   u'TS_DEC_BOILER_WOOD': u'THE',
                   u'TS_DEC_BOILER_OIL': u'THE',
                   u'TS_DHN_DAILY': u'THE',  # TO DO
                   u'TS_DHN_SEASONAL': u'',  # TO DO
                   u'TS_HIGH_TEMP': u'',
                   u'SEASONAL_NG': u'GAS',  # TO DO
                   u'SEASONAL_H2': u'HYD',
                   u'H2_STORAGE': u'HYD',
                   u'H2_ELECTROLYSIS': u'HYD',
                   u'HABER_BOSCH': u''}  # TO DO

mapping['ES']['RESOURCE'] = {u'BIODIESEL': u'BIODIESEL',
                       u'BIOETHANOL': u'BIOETHANOL',
                       u'CO2_ATM ': u'CO2_ATM',
                       u'CO2_CAPTURED': u'CO2_CAPTURED',
                       u'CO2_EMISSIONS': u'CO2_EMISSIONS',
                       u'CO2_INDUSTRY ': u'CO2_INDUSTRY',
                       u'COAL': u'HRD',
                       u'DIESEL': u'OIL',
                       u'ELECTRICITY': u'ELECTRICITY',
                       u'ELEC_EXPORT': u'ELEC_EXPORT',
                       u'GASOLINE': u'GASOLINE',
                       u'H2': u'HYD',
                       u'LFO': u'LFO',
                       u'NG': u'GAS',
                       u'GAS': u'GAS',
                       u'AMMONIA': u'AMO',
                       u'RES_GEO': u'GEO',
                       u'RES_HYDRO': u'WAT',
                       u'RES_SOLAR': u'SUN',
                       u'RES_WIND': u'WIN',
                       u'SLF': u'SLF',
                       u'SNG': u'SNG',
                       u'URANIUM': u'NUC',
                       u'WASTE': u'WST',
                       u'WET_BIOMASS': u'WET_BIOMASS',
                       u'WOOD': u'WOOD'}

# DICO used to get efficiency of tech in layers_in_out
mapping['ES']['FUEL_ES'] = {u'CCGT': u'GAS',
                      u'CCGT_AMMONIA': u'AMMONIA',
                      u'OCGT': u'GAS',
                      u'COAL_IGCC': u'COAL',
                      u'COAL_US': u'COAL',
                      u'PV': u'RES_SOLAR',
                      u'GEOTHERMAL': u'RES_GEO ',
                      u'NUCLEAR': u'URANIUM',
                      u'HYDRO_RIVER': u'RES_HYDRO',
                      u'NEW_HYDRO_RIVER': u'RES_HYDRO',
                      u'WIND': u'RES_WIND',  # IF WIND is not specified, WIND is asumed to be ONSHORE
                      u'WIND_OCapitalfCapitalfSHORE': u'RES_WIND',
                      u'WIND_OFFSHORE': u'RES_WIND',
                      u'WIND_ONSHORE': u'RES_WIND',
                      u'IND_COGEN_GAS': u'GAS',
                      u'IND_COGEN_WOOD': u'WOOD',
                      u'IND_COGEN_WASTE': u'WASTE',
                      u'IND_BOILER_GAS': u'GAS',
                      u'IND_BOILER_WOOD': u'WOOD',
                      u'IND_BOILER_OIL': u'LFO',
                      u'IND_BOILER_COAL': u'COAL',
                      u'IND_BOILER_WASTE': u'WASTE',
                      u'IND_DIRECT_ELEC': u'ELECTRICITY',  # P2HT ?
                      u'DHN_HP_ELEC': u'ELECTRICITY',  # P2HT ?
                      u'DHN_COGEN_GAS': u'GAS',
                      u'DHN_COGEN_WOOD': u'WOOD',
                      u'DHN_COGEN_WASTE': u'WASTE',
                      u'DHN_COGEN_WET_BIOMASS': u'WET_BIOMASS',
                      u'DHN_BOILER_GAS': u'GAS',
                      u'DHN_BOILER_WOOD': u'WOOD',
                      u'DHN_BOILER_OIL': u'LFO',
                      u'DHN_DEEP_GEO': u'RES_GEO ',
                      u'DHN_SOLAR': u'RES_SOLAR',
                      u'DEC_HP_ELEC': u'ELECTRICITY',
                      u'DEC_THHP_GAS': u'GAS',
                      u'DEC_COGEN_GAS': u'GAS',
                      u'DEC_COGEN_OIL': u'LFO',
                      u'DEC_ADVCOGEN_GAS': u'GAS',
                      u'DEC_ADVCOGEN_H2': u'H2',
                      u'DEC_BOILER_GAS': u'GAS',
                      u'DEC_BOILER_WOOD': u'WOOD',
                      u'DEC_BOILER_OIL': u'LFO',
                      u'DEC_SOLAR': u'RES_SOLAR',
                      u'DEC_DIRECT_ELEC': u'ELECTRICITY',
                      u'PHS': u'RES_HYDRO',  # STO ? Efficiency ?
                      u'PHES': u'RES_HYDRO',  # STO ? Efficiency ?
                      u'DAM_STORAGE': u'RES_HYDRO',  # STO ? Efficiency ?
                      u'BATT_LI': u'ELECTRICITY',  # STO ? Efficiency ?
                      u'BEV_BATT': u'ELECTRICITY',  # STO ? Efficiency ?
                      u'PHEV_BATT': u'ELECTRICITY',  # STO ? Efficiency ?
                      u'TS_DEC_DIRECT_ELEC': u'',  # P2HT ?  #Do I need to specify a fuel for Thermal Storage ?
                      u'TS_DEC_HP_ELEC': u'',  # P2HT ?
                      u'TS_DEC_THHP_GAS': u'',  # STO ? Efficiency ?
                      u'TS_DEC_COGEN_GAS': u'',  # STO ? Efficiency ?
                      u'TS_DEC_COGEN_OIL': u'',  # STO ? Efficiency ?
                      u'TS_DEC_ADVCOGEN_GAS': u'',  # STO ? Efficiency ?
                      u'TS_DEC_ADVCOGEN_H2': u'',  # STO ? Efficiency ?
                      u'TS_DEC_BOILER_GAS': u'',  # STO ? Efficiency ?
                      u'TS_DEC_BOILER_WOOD': u'',  # STO ? Efficiency ?
                      u'TS_DEC_BOILER_OIL': u'',  # STO ? Efficiency ?
                      u'TS_DHN_DAILY': u'',  # TO DO #STO ? Efficiency ?
                      u'TS_DHN_SEASONAL': u'',  # TO DO #STO ? Efficiency ?
                      u'TS_HIGH_TEMP': u'',
                      u'SEASONAL_NG': u'',  # TO DO #STO ? Efficiency ?
                      u'SEASONAL_H2': u'',
                      u'H2_STORAGE': u'',
                      u'OCGT_GAS': u'GAS',
                      u'CCGT_GAS': u'GAS',
                      u'STUR_GAS': u'GAS',
                      u'H2_ELECTROLYSIS': u'ELECTRICITY',
                      u'HABER_BOSCH': u'AMMONIA'}  # TO DO #STO ? Efficiency ?

mapping['ES']['CHP_HEAT'] = {u'IND_COGEN_GAS': u'HEAT_HIGH_T',
                       u'IND_COGEN_WOOD': u'HEAT_HIGH_T',
                       u'IND_COGEN_WASTE': u'HEAT_HIGH_T',
                       u'DHN_COGEN_GAS': u'HEAT_LOW_T_DHN',
                       u'DHN_COGEN_WOOD': u'HEAT_LOW_T_DHN',
                       u'DHN_COGEN_WASTE': u'HEAT_LOW_T_DHN',
                       u'DHN_COGEN_WET_BIOMASS': u'HEAT_LOW_T_DHN',
                       u'DEC_COGEN_GAS': u'HEAT_LOW_T_DECEN',
                       u'DEC_COGEN_OIL': u'HEAT_LOW_T_DECEN',
                       u'DEC_ADVCOGEN_GAS': u'HEAT_LOW_T_DECEN',
                       u'DEC_ADVCOGEN_H2': u'HEAT_LOW_T_DECEN'}

mapping['ES']['HEAT_ONLY_HEAT'] = {u'IND_BOILER_GAS': u'HEAT_HIGH_T',
                             u'IND_BOILER_WOOD': u'HEAT_HIGH_T',
                             u'IND_BOILER_WASTE': u'HEAT_HIGH_T',
                             u'IND_BOILER_OIL': u'HEAT_HIGH_T',
                             u'IND_BOILER_COAL': u'HEAT_HIGH_T',
                             u'DHN_BOILER_GAS': u'HEAT_LOW_T_DHN',
                             u'DHN_BOILER_WOOD': u'HEAT_LOW_T_DHN',
                             u'DHN_BOILER_WASTE': u'HEAT_LOW_T_DHN',
                             u'DHN_BOILER_OIL': u'HEAT_LOW_T_DHN',
                             u'DHN_DEEP_GEO': u'HEAT_LOW_T_DHN',
                             u'DHN_SOLAR': u'HEAT_LOW_T_DHN',
                             u'DEC_BOILER_GAS': u'HEAT_LOW_T_DECEN',
                             u'DEC_BOILER_WOOD': u'HEAT_LOW_T_DECEN',
                             u'DEC_BOILER_OIL': u'HEAT_LOW_T_DECEN',
                             u'DEC_SOLAR': u'HEAT_LOW_T_DECEN',
                             u'DEC_THHP_GAS': u'HEAT_LOW_T_DECEN'
                             }

mapping['ES']['P2HT_HEAT'] = {u'IND_DIRECT_ELEC': u'HEAT_HIGH_T',
                        u'DHN_HP_ELEC': u'HEAT_LOW_T_DHN',
                        u'DEC_HP_ELEC': u'HEAT_LOW_T_DECEN',
                        u'DEC_DIRECT_ELEC': u'HEAT_LOW_T_DECEN'
                        }
# u'TS_DEC_HP_ELEC': u''} - Thermal Storage : is P2HT techno ?

# That dictionary could be automatize for DEC_P2HT - IS IT BETTER THOUGH ? - TO CHECK
mapping['ES']['THERMAL_STORAGE'] = {u'DEC_DIRECT_ELEC': u'TS_DEC_DIRECT_ELEC',
                              u'DEC_HP_ELEC': u'TS_DEC_HP_ELEC',
                              u'DEC_THHP_GAS': u'TS_DEC_THHP_GAS',
                              u'DEC_COGEN_GAS': u'TS_DEC_COGEN_GAS',
                              u'DEC_COGEN_OIL': u'TS_DEC_COGEN_OIL',
                              u'DEC_ADVCOGEN_GAS': u'TS_DEC_ADVCOGEN_GAS',
                              u'DEC_ADVCOGEN_H2': u'TS_DEC_ADVCOGEN_H2',
                              u'DEC_BOILER_GAS': u'TS_DEC_BOILER_GAS',
                              u'DEC_BOILER_WOOD': u'TS_DEC_BOILER_WOOD',
                              u'DEC_BOILER_OIL': u'TS_DEC_BOILER_OIL'}

# That dictionary could be automatize for DEC_P2HT - IS IT BETTER THOUGH ? - TO CHECK
mapping['ES']['P2GS_STORAGE'] = {u'H2_ELECTROLYSIS': u'H2_STORAGE'}

# mapping of cvost of fuels
mapping['ES']['FUEL_COST'] = {u'AMMONIA': u'PriceOfAmmonia',
                        u'URANIUM': u'PriceOfNuclear',
                        u'COAL': u'PriceOfBlackCoal',
                        u'GAS': u'PriceOfGas',
                        u'LFO': u'PriceOfFuelOil',
                        u'WOOD': u'PriceOfBiomass'}

########################################################################################################################
