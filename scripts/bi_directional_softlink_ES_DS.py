# Add the root folder of Dispa-SET-side tools to the path so that the library can be loaded:
import logging
import os
import pickle
import sys
from pathlib import Path
from tqdm import tqdm
from tqdm import trange

import dispaset as ds
import energyscope as es
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import enlopy as el

import dispa_link as dl

sys.path.append(os.path.abspath('..'))

# %% #############################################
############## Folder and Path setup #############
##################################################
dst_path = Path(__file__).parents[1]
# Typical units
typical_units_folder = dst_path / 'Inputs' / 'EnergyScope'

# Energy Scope
ES_folder = dst_path.parent / 'EnergyScope'
DL_folder = dst_path.parent / 'Dispa-LINK'

target_year = 2050
config_link = {'DateRange': dl.get_date_range(target_year), 'TypicalUnits': typical_units_folder}
data_folder = ES_folder / 'Data' / str(target_year)
ES_path = ES_folder / 'energyscope' / 'STEP_2_Energy_Model'
step1_output = ES_folder / 'energyscope' / 'STEP_1_TD_selection' / 'TD_of_days.out'

dispaset_version = '2.5_BS'  # 2.5 or 2.5_BS

# %% ###################################
########### Editable inputs ############
########################################
case_name = 'UTOPIA'  # UTOPIA or DYSTOPIA
separator = ';'
reserve_dumping = 0.5
seasonal_storage_days = 7
ccgt_share = 0.05

initialize_ES = False
run_loop = False

# Assign soft-linking iteration parameters
max_loops = 5

# EnergyScope inputs
if case_name == 'UTOPIA':
    scenario = 12500
elif case_name == 'DYSTOPIA':
    scenario = 1e7
else:
    logging.ERROR('Wrong scenario selected. Please selecet either UTOPIA or DYSTOPIA')
    sys.exit(1)
# case_study = dispaset_version + '_' + str(scenario) + '_ELEImp=0_WIND_ONOFFSHORE=70_LOCALAMONIA_NUC=4_CURT=0_ENS=2k_BS'
case_study = case_name + '_' + dispaset_version + '_' + str(scenario) + '_RESERVE_dumping=' + str(1 - reserve_dumping) + \
             '_SSTOR=' + str(seasonal_storage_days) + '_CCGTshare=' + str(ccgt_share) + '_final'

config_es = {'case_study': case_study + '_loop_0', 'comment': 'Test with low emissions', 'run_ES': False,
             'import_reserves': '', 'importing': True, 'printing': False, 'printing_td': False, 'GWP_limit': scenario,
             'data_folder': data_folder, 'ES_folder': ES_folder, 'ES_path': ES_path, 'step1_output': step1_output,
             'all_data': dict(), 'Working_directory': os.getcwd(), 'reserves': pd.DataFrame(), 'user_defined': dict()}

ES_output = config_es['ES_folder'] / 'case_studies' / config_es['case_study'] / 'output'
# %% ####################################
#### Update and Execute EnergyScope ####
########################################
if run_loop:
    # Reading the data
    config_es['all_data'] = es.run_ES(config_es)
    # Resource limits
    config_es['all_data']['Resources'].loc['ELECTRICITY', 'avail'] = 0
    config_es['all_data']['Resources'].loc['ELEC_EXPORT', 'avail'] = 0
    config_es['all_data']['Resources'].loc['AMMONIA', 'avail'] = 0
    config_es['all_data']['Resources'].loc['AMMONIA_RE', 'avail'] = 0
    if case_name == 'UTOPIA':
        config_es['all_data']['Resources'].loc['WOOD', 'avail'] = 25000
        config_es['all_data']['Resources'].loc['WET_BIOMASS', 'avail'] = 40000
        config_es['all_data']['Resources'].loc['COAL', 'avail'] = 30000
        config_es['all_data']['Resources'].loc['WASTE', 'avail'] = 30000
    elif case_name == 'DYSTOPIA':
        config_es['all_data']['Resources'].loc['WOOD', 'avail'] = 100000
        config_es['all_data']['Resources'].loc['WET_BIOMASS', 'avail'] = 100000
        config_es['all_data']['Resources'].loc['COAL', 'avail'] = 100000
        config_es['all_data']['Resources'].loc['WASTE', 'avail'] = 100000
    # Technology limits
    config_es['all_data']['Technologies'].loc['CCGT_AMMONIA', ['f_max', 'fmax_perc']] = 1e15, 0.1
    config_es['all_data']['Technologies'].loc['NUCLEAR', ['f_max', 'fmax_perc']] = 1e15, 0.1
    config_es['all_data']['Technologies'].loc['CCGT', ['f_max', 'fmax_perc']] = 1e15, ccgt_share
    config_es['all_data']['Technologies'].loc['COAL_US', ['f_max', 'fmax_perc']] = 1e15, 0.1
    config_es['all_data']['Technologies'].loc['COAL_IGCC', ['f_max', 'fmax_perc']] = 1e15, 0.1
    config_es['all_data']['Technologies'].loc['HYDRO_RIVER', ['f_max', 'fmin_perc', 'fmax_perc']] = 1e15, 0.15, 1
    config_es['all_data']['Technologies'].loc['PV', 'f_max'] = 1e15
    config_es['user_defined']['solar_area'] = 1e15
    config_es['user_defined']['curt_perc_cap'] = 0
    # Allow infinite WIND_ONSHORE
    config_es['all_data']['Technologies'].loc['WIND_ONSHORE', 'f_max'] = 1e15
    config_es['all_data']['Technologies'].loc['WIND_OFFSHORE', ['f_min', 'f_max']] = 10, 1e15
    # Allow infinite PHS
    config_es['all_data']['Technologies'].loc['PHS', ['f_max', 'fmax_perc']] = 120, 0.15
    # Change storage parameters
    config_es['all_data']['Storage_characteristics'].loc['H2_STORAGE', ['storage_charge_time',
                                                                        'storage_discharge_time']] = 24 * seasonal_storage_days, 24 * seasonal_storage_days / 3
    config_es['all_data']['Technologies'].loc['H2_STORAGE', ['c_inv',
                                                             'c_maint']] = 3.66 * 6 / 24 / seasonal_storage_days, 0.39 * 6 / 24 / seasonal_storage_days
    config_es['all_data']['Storage_characteristics'].loc['TS_DHN_SEASONAL', ['storage_charge_time',
                                                                             'storage_discharge_time']] = 24 * seasonal_storage_days, 24 * seasonal_storage_days
    config_es['all_data']['Technologies'].loc['TS_DHN_SEASONAL', ['c_inv',
                                                                  'c_maint']] = 0.51718 * 150 / 24 / seasonal_storage_days, 0.00283 * 150 / 24 / seasonal_storage_days
    # Change prices
    config_es['all_data']['Resources'].loc['GAS', 'c_op'] = 0.2

    # Printing and running
    config_es['importing'] = False
    config_es['printing'] = True
    config_es['printing_td'] = True
    config_es['run_ES'] = True
    if initialize_ES:
        config_es['all_data'] = es.run_ES(config_es)

    # %% Assign empty variables (to be populated inside the loop)
    ds_inputs = {'Capacities': dict(), 'Costs': dict(), 'ElectricityDemand': dict(), 'HeatDemand': dict(),
                 'XFixDemand': dict(), 'XVarDemand': dict(), 'XFixSupply': dict(), 'XVarSupply': dict(),
                 'OutageFactors': dict(), 'ReservoirLevels': dict(), 'AvailabilityFactors': dict(),
                 'EVDemand': dict()}
    inputs_mts, results_mts = dict(), dict()
    inputs, results, GWP_op, reserves, shed_load, Price_CO2 = dict(), dict(), dict(), dict(), dict(), dict()
    LL, Curtailment = pd.DataFrame(), pd.DataFrame()
    iteration = {}
    es_outputs = dict()

    # %% ###################################
    ######## Soft-linking procedure ########
    ########################################
    LostLoad = pd.DataFrame()
    ShedLoad = pd.DataFrame()
    Curtailment = pd.DataFrame()
    Reserve = pd.DataFrame()
    iterations = ['Initialization', 'Reserve', 'Iter1', 'Iter2', 'Iter3', 'Iter4', 'Iter5', 'Iter6']
    for i in range(max_loops):
        config_es['case_study'] = case_study + '_loop_' + str(i)
        print('loop number', i)

        # Dynamic Data - to be modified in a loop
        # Compute the actual average annual emission factors for each resource
        # TODO automate
        GWP_op[i] = es.compute_gwp_op(config_es['data_folder'], ES_folder / 'case_studies' / config_es['case_study'])
        GWP_op[i].to_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' / 'GWP_op.txt', sep='\t')

        # %% Reading the ES outputs
        es_outputs[i] = es.read_outputs(config_es['case_study'], True, [])
        es_outputs[i]['GWP_op'] = GWP_op[i]
        es_outputs[i]['timeseries'] = pd.read_csv(config_es['data_folder'] / 'Time_series.csv', header=0, sep=separator)
        es_outputs[i]['demands'] = pd.read_csv(config_es['data_folder'] / 'Demand.csv', sep=separator)
        es_outputs[i]['layers_in_out'] = pd.read_csv(config_es['data_folder'] / 'Layers_in_out.csv', sep=separator,
                                                     index_col='param layers_in_out:')
        es_outputs[i]['storage_characteristics'] = pd.read_csv(config_es['data_folder'] / 'Storage_characteristics.csv',
                                                               sep=separator, index_col='param :')
        es_outputs[i]['storage_eff_in'] = pd.read_csv(config_es['data_folder'] / 'Storage_eff_in.csv',
                                                      sep=separator, index_col='param storage_eff_in :')
        es_outputs[i]['storage_eff_out'] = pd.read_csv(config_es['data_folder'] / 'Storage_eff_out.csv',
                                                       sep=separator, index_col='param storage_eff_out:')
        es_outputs[i]['high_t_Layers'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                     'hourly_data' / 'layer_HEAT_HIGH_T.txt', delimiter='\t',
                                                     index_col=[0, 1])
        es_outputs[i]['low_t_decen_Layers'] = pd.read_csv(
            ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
            'hourly_data' / 'layer_HEAT_LOW_T_DECEN.txt', delimiter='\t',
            index_col=[0, 1])
        es_outputs[i]['low_t_dhn_Layers'] = pd.read_csv(
            ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
            'hourly_data' / 'layer_HEAT_LOW_T_DHN.txt', delimiter='\t',
            index_col=[0, 1])

        # TODO update with new possibility of changing output folder
        # Clean ES outputs i.e. remove blank spaces
        es_outputs[i]['assets'] = dl.clean_blanks(es_outputs[i]['assets'])
        es_outputs[i]['year_balance'] = dl.clean_blanks(es_outputs[i]['year_balance'])
        es_outputs[i]['layers_in_out'] = dl.clean_blanks(es_outputs[i]['layers_in_out'])
        es_outputs[i]['storage_characteristics'] = dl.clean_blanks(es_outputs[i]['storage_characteristics'])
        es_outputs[i]['storage_eff_in'] = dl.clean_blanks(es_outputs[i]['storage_eff_in'])
        es_outputs[i]['storage_eff_out'] = dl.clean_blanks(es_outputs[i]['storage_eff_out'])
        es_outputs[i]['high_t_Layers'] = dl.clean_blanks(es_outputs[i]['high_t_Layers'], idx=False)
        es_outputs[i]['low_t_decen_Layers'] = dl.clean_blanks(es_outputs[i]['low_t_decen_Layers'], idx=False)
        es_outputs[i]['low_t_dhn_Layers'] = dl.clean_blanks(es_outputs[i]['low_t_dhn_Layers'], idx=False)

        # transforming TD time series into yearly time series
        td_df = dl.process_TD(td_final=pd.read_csv(config_es['step1_output'], header=None))

        # %% compute fuel prices according to the use of RE vs NON-RE fuels
        resources = config_es['all_data']['Resources']
        df = es_outputs[i]['year_balance'].loc[
            resources.index, es_outputs[i]['year_balance'].columns.isin(list(resources.index))]
        ds_inputs['Costs'][i] = (df.mul(resources.loc[:, 'c_op'], axis=0).sum(axis=0) /
                                 df.sum(axis=0)).fillna(resources.loc[:, 'c_op'])

        # %% Compute availability factors and scaled inflows
        ds_inputs['AvailabilityFactors'][i] = dl.get_availability_factors(es_outputs[i], config_link['DateRange'],
                                                                          file_name_af='AF_2015_ES',
                                                                          file_name_sif='IF_2015_ES')

        # %% Compute electricity demand
        es_outputs[i]['electricity_layers'] = pd.read_csv(
            ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
            'hourly_data' / 'layer_ELECTRICITY.txt', delimiter='\t',
            index_col=[0, 1])
        ds_inputs['ElectricityDemand'][i] = dl.get_electricity_demand(es_outputs[i], td_df, config_link['DateRange'],
                                                                      file_name='2015_ES')

        # %% compute H2 yearly consumption and power capacity of electrolyser
        es_outputs[i]['h2_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                'hourly_data' / 'layer_H2.txt', delimiter='\t', index_col=[0, 1])
        es_outputs[i]['ammonia_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                     'hourly_data' / 'layer_AMMONIA.txt', delimiter='\t',
                                                     index_col=[0, 1])
        es_outputs[i]['gas_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                 'hourly_data' / 'layer_GAS.txt', delimiter='\t', index_col=[0, 1])
        es_outputs[i]['wood_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                  'hourly_data' / 'layer_WOOD.txt', delimiter='\t', index_col=[0, 1])
        es_outputs[i]['lfo_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                 'hourly_data' / 'layer_LFO.txt', delimiter='\t', index_col=[0, 1])
        es_outputs[i]['coal_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                  'hourly_data' / 'layer_COAL.txt', delimiter='\t', index_col=[0, 1])
        es_outputs[i]['waste_layer'] = pd.read_csv(ES_folder / 'case_studies' / config_es['case_study'] / 'output' /
                                                   'hourly_data' / 'layer_WASTE.txt', delimiter='\t', index_col=[0, 1])

        ds_inputs = dl.merge_timeseries_x(ds_inputs, es_outputs[i], td_df, config_link['DateRange'], dispaset_version,
                                          i)
        ds_inputs['XFixDemand'][i] = ds_inputs['XFixDemand'][i].add(-ds_inputs['XFixSupply'][i], fill_value=0)

        # %% Get capacities from ES, map them to DS with external typical unit database
        typical_units = pd.read_csv(config_link['TypicalUnits'] / 'Typical_Units.csv')
        ds_inputs['Capacities'][i] = dl.get_capacities_from_es(es_outputs[i], typical_units=typical_units, td_df=td_df,
                                                               technology_threshold=0.1,
                                                               dispaset_version=dispaset_version,
                                                               config_link=config_link, ds_inputs=ds_inputs,
                                                               i=i)  # TODO: remove really small technologies

        ds_inputs['EVDemand'][i] = dl.get_ev_demand(es_outputs[i], td_df, ds_inputs['Capacities'][i],
                                                    config_link['DateRange'], file_name='EV_Demand')

        # %% Assign outage factors for technologies that generate more than available
        ds_inputs['OutageFactors'][i] = dl.get_outage_factors(config_es, es_outputs[i], drange=config_link['DateRange'],
                                                              local_res=['WASTE', 'WOOD', 'WET_BIOMASS'], td_df=td_df)

        # %% Compute heat demand for different heating layers
        ds_inputs['HeatDemand'][i] = dl.get_heat_demand(es_outputs[i], td_df, config_link['DateRange'],
                                                        countries=['ES'], file_name='2015_ES_th',
                                                        dispaset_version=dispaset_version)

        if dispaset_version == '2.5_BS':
            dl.write_csv_files('BoundarySectorDemand', ds_inputs['XFixDemand'][i], 'BoundarySectorDemand',
                               index=True, write_csv=True)
            dl.write_csv_files('BoundarySectorVarDemand', ds_inputs['XVarDemand'][i], 'BoundarySectorVarDemand',
                               index=True, write_csv=True)
            dl.write_csv_files('BoundarySectorVarSupply', ds_inputs['XVarSupply'][i], 'BoundarySectorVarSupply',
                               index=True, write_csv=True)

        # %% Assign storage levels
        ds_inputs['ReservoirLevels'][i] = dl.get_soc(es_outputs[i], config_es, config_link['DateRange'])

        # %% ###################################
        ########## Execute Dispa-SET ##########
        #######################################
        # Load the appropriate configuration file (2.5 or boundary sector version)
        if dispaset_version == '2.5':
            config = ds.load_config('../ConfigFiles/Config_EnergyScope.xlsx')
            # config['default']['CostCurtailment'] = abs(es_outputs[i]['Curtailment_cost'].loc['Curtailment_cost',
            #                                                                               'Curtailment_cost'] * 1000)
            config['default']['CostCurtailment'] = 0
        if dispaset_version == '2.5_BS':
            config = ds.load_config('../ConfigFiles/Config_EnergyScope_BS.xlsx')
            config['default']['CostCurtailment'] = 0
        # Assign new input csv files if needed
        config['ReservoirLevels'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'ReservoirLevels' / '##' /
                                        'ReservoirLevels.csv')

        config['SimulationDirectory'] = str(DL_folder / 'Simulations' / str(case_study + '_loop_' + str(i)))
        config['default']['PriceOfCO2'] = abs(es_outputs[i]['CO2_cost'].loc['CO2_cost', 'CO2_cost'] * 1000)

        for j in dl.mapping['ES']['FUEL_COST']:
            config['default'][dl.mapping['ES']['FUEL_COST'][j]] = ds_inputs['Costs'][i].loc[j] * 1000

        # %% Dispa-SET version 2.5
        if dispaset_version == '2.5':
            config['H2FlexibleDemand'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'H2_demand' / 'ES' /
                                             'H2_demand.csv')
            config['H2FlexibleCapacity'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'H2_demand' / 'ES' /
                                               'PtLCapacities.csv')
            config['Outages'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'OutageFactor' / '##' /
                                    'OutageFactor.csv')

        # %% Dispa-SET version boundary sector
        if dispaset_version == '2.5_BS':
            config['SectorXDemand'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'BoundarySectorDemand' /
                                          'ES' / 'BoundarySectorDemand.csv')
            config['HeatDemand'] = ''
            config['BoundarySectorData'] = str(
                DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'BoundarySectorInputs' /
                'ES' / 'BoundarySectorInputs.csv')
            # config['BoundarySectorNTC'] = 139
            # config['BoundarySectorInterconnections'] = 140
            config['SectorXFlexibleDemand'] = str(
                DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'BoundarySectorVarDemand' / 'ES' /
                'BoundarySectorVarDemand.csv')
            config['SectorXFlexibleSupply'] = str(
                DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'BoundarySectorVarSupply' / 'ES' /
                'BoundarySectorVarSupply.csv')
            config['BoundarySectorMaxSpillage'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' / 'H2_demand' /
                                                      'H2_demand.csv')
            # config['CostXNotServed'] = 170
            config['ReservoirScaledOutflows'] = str(DL_folder / 'Outputs' / 'EnergyScope' / 'Database' /
                                                    'TotalLoadValue' / 'ES' / 'EV_Demand.csv')

        # Build the simulation environment:
        SimData = ds.build_simulation(config)

        # Solve using GAMS:
        _ = ds.solve_GAMS(config['SimulationDirectory'], config['GAMS_folder'])

        # Load the simulation results:
        inputs_mts[i], results_mts[i] = ds.get_sim_results(config['SimulationDirectory'], cache=False,
                                                           inputs_file='Inputs_MTS.p',
                                                           results_file='Results_MTS.gdx')
        inputs[i], results[i] = ds.get_sim_results(config['SimulationDirectory'], cache=False)

        # %% Save DS results to pickle file
        ES_output = ES_folder / 'case_studies' / config_es['case_study'] / 'output'
        with open(ES_output / 'DS_Results.p', 'wb') as handle:
            pickle.dump(inputs[i], handle, protocol=pickle.HIGHEST_PROTOCOL)
            pickle.dump(results[i], handle, protocol=pickle.HIGHEST_PROTOCOL)

        # TODO: reading and storing ESTD results

        # %% Run ES with reserves (2nd+ run)
        config_es['case_study'] = case_study + '_loop_' + str(i + 1)
        config_es['import_reserves'] = 'from_df'
        # TODO: check if leap year can be introduced
        reserves[i] = pd.DataFrame(results[i]['OutputDemand_3U'].values / 1000, columns=['end_uses_reserve'],
                                   index=np.arange(1, 8761, 1))
        # Check if it is necessary to apply additional reserve requirements
        if i >= 1:
            if results[i]['OutputShedLoad'].empty:
                shed_load[i] = pd.DataFrame(0, columns=['end_uses_reserve'], index=np.arange(1, 8761, 1))
            else:
                lost_load = results[i]['OutputShedLoad'].add(results[0]['LostLoad_MaxPower'], fill_value=0)
                shed_load[i] = pd.DataFrame(lost_load.values / 1000, columns=['end_uses_reserve'],
                                            index=np.arange(1, 8761, 1))
            config_es['reserves'] = config_es['reserves'] + shed_load[i].max() * (1 - reserve_dumping)
        else:
            config_es['reserves'] = reserves[i]

        with open('ES_reserve_' + case_study + '_loop_' + str(i) + '.p', 'wb') as handle:
            pickle.dump(config_es['reserves'], handle, protocol=pickle.HIGHEST_PROTOCOL)

        LL = pd.concat([LL, results[i]['OutputShedLoad']], axis=1)
        Curtailment = pd.concat([Curtailment, results[i]['OutputCurtailedPower']], axis=1)

        if not results[i]['OutputShedLoad'].empty:
            print('Another iteration required')
        else:
            print('Final convergence occurred in loop: ' + str(i) + '. Soft-linking is now complete')
            break

        # %% Brake loop at the maximum loops specified
        if i == max_loops - 1:
            print('Last opt')
        else:
            config_es['all_data'] = es.run_ES(config_es)

    with open(case_study + '.p', 'wb') as handle:
        pickle.dump(inputs, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(inputs_mts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(results_mts, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(config_es, handle, protocol=pickle.HIGHEST_PROTOCOL)
        pickle.dump(es_outputs, handle, protocol=pickle.HIGHEST_PROTOCOL)

else:
    with open(case_study + '.p', 'rb') as handle:
        inputs = pickle.load(handle)
        results = pickle.load(handle)
        inputs_mts = pickle.load(handle)
        results_mts = pickle.load(handle)
        config_es = pickle.load(handle)
        es_outputs = pickle.load(handle)

# %% ########################################################################
# ####################### LDC comparison plots ##############################
#############################################################################
# es_outputs = dict()
# # config_es['all_data'] = es.run_ES(config_es)
# for i in range(0, max_loops):
#     es_outputs[i] = es.read_outputs(case_study + '_loop_' + str(i), hourly_data=True,
#                                     layers=['layer_ELECTRICITY', 'layer_reserve_ELECTRICITY'])

td_df = dl.process_TD(td_final=pd.read_csv(config_es['step1_output'], header=None))
el_layers = es.from_td_to_year(es_outputs[0]['electricity_layers'].dropna(axis=1),
                               td_df.rename({'TD': 'TD_number', 'hour': 'H_of_D'}, axis=1))
es.plot_layer_elec_td(layer_elec=es_outputs[0]['electricity_layers'].dropna(axis=1), title='Layer electricity',
                      tds=np.arange(1, 13), reorder_elec=None, figsize=(15, 7))
# es.hourly_plot(plotdata= es.from_td_to_year(es_outputs[0]['layer_ELECTRICITY'].dropna(axis=1), td_df.rename({'TD': 'TD_number', 'hour': 'H_of_D'}, axis=1)), title='', xticks=None, figsize=(17,7), colors=None, nbr_tds=12, show=True)

positive_el_layers = el_layers.loc[:, el_layers.select_dtypes(include=[np.number]).ge(0).all(0)]
positive_el_layers = positive_el_layers.loc[:, (positive_el_layers != 0).any(axis=0)]

negative_el_layers = -el_layers.loc[:, el_layers.select_dtypes(include=[np.number]).le(0).all(0)]
negative_el_layers = negative_el_layers.loc[:, (negative_el_layers != 0).any(axis=0)]

aa = negative_el_layers['END_USE'].sort_values(ascending=False).reset_index(drop=True)
aa.plot()
plt.show()

ds_gen = results[0]['OutputPower'] / 1000

generation = pd.concat(
    [ds_gen.sum(axis=1).reset_index(drop=True), positive_el_layers.sum(axis=1).reset_index(drop=True)], axis=1)
ldc = pd.concat([ds_gen.sum(axis=1).sort_values(ascending=False).reset_index(drop=True),
                 positive_el_layers.sum(axis=1).sort_values(ascending=False).reset_index(drop=True)], axis=1)
ldc.rename(columns={0: 'DS', 1: 'ES'}, inplace=True)
ldc.plot()
plt.show()

ldc_ds = pd.concat([negative_el_layers.sum(axis=1).sort_values(ascending=False).reset_index(drop=True),
                    results[0]['TotalDemand']['ES'].sort_values(ascending=False).reset_index(drop=True) / 1000], axis=1)
ldc_ds.rename(columns={0: 'DS_GEN', 1: 'DS_DEM'}, inplace=True)
ldc_ds.plot()
plt.show()


def get_results(results, i, LostLoad, ShedLoad, Curtailment, Reserve, Error):
    iter_name = iterations[i]
    if not results[i]['OutputShedLoad'].empty:
        ShedLoad.loc[:, iter_name] = results[i]['OutputShedLoad']
    else:
        ShedLoad.loc[:, iter_name] = pd.DataFrame(np.zeros((8760, 1)), index=ShedLoad.index)
    if not results[i]['LostLoad_MaxPower'].empty:
        LostLoad.loc[:, iter_name] = pd.DataFrame(results[i]['LostLoad_MaxPower'], index=ShedLoad.index).fillna(0)
    else:
        LostLoad.loc[:, iter_name] = pd.DataFrame(np.zeros((8760, 1)), index=ShedLoad.index)
    if not results[i]['OutputCurtailedPower'].empty:
        Curtailment.loc[:, iter_name] = results[i]['OutputCurtailedPower']
    else:
        Curtailment.loc[:, iter_name] = pd.DataFrame(np.zeros((8760, 1)), index=ShedLoad.index)
    if not results[i]['OutputDemand_3U'].empty:
        Reserve.loc[:, iter_name] = results[i]['OutputDemand_3U']
    else:
        Reserve.loc[:, iter_name] = pd.DataFrame(np.zeros((8760, 1)), index=ShedLoad.index)
    Error.loc[:, iter_name] = pd.DataFrame(results[i]['OutputOptimizationCheck'])
    return LostLoad, ShedLoad, Curtailment, Reserve, Error


LostLoad = pd.DataFrame()
ShedLoad = pd.DataFrame()
Curtailment = pd.DataFrame()
Reserve = pd.DataFrame()
Error = pd.DataFrame()
iterations = ['Initialization', 'Reserve', 'Iter1', 'Iter2', 'Iter3']
for i in range(max_loops):
    LostLoad, ShedLoad, Curtailment, Reserve, Error = get_results(results, i, LostLoad, ShedLoad, Curtailment, Reserve, Error)

LL = ShedLoad.add(LostLoad, axis=1, fill_value=0)
LL = pd.DataFrame(LL, columns=iterations)

a = LL != 0
b = Curtailment != 0

LL_cum = LL.cumsum().where(a).ffill().fillna(0) - LL.cumsum().where(~a).ffill().fillna(0)
Curt_cum = Curtailment.cumsum().where(b).ffill().fillna(0) - Curtailment.cumsum().where(~b).ffill().fillna(0)

compare = pd.DataFrame()
for i in range(max_loops):
    iter_name = iterations[i]
    compare[iter_name] = Curt_cum.iloc[:, i] - LL_cum.iloc[:, i]
    compare[iter_name] = compare[iter_name].cumsum()

# Load duration curve plots
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

pd.plotting.register_matplotlib_converters()
# LL load duration curve
LL_ldc = pd.DataFrame(-np.sort(-LL.values, axis=0), index=LL.index,
                      columns=iterations).reset_index(drop=True)

figsize = (13, 7)
fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=figsize, frameon=True,  # 14 4*2
                         gridspec_kw={'height_ratios': [1, 1], 'hspace': 0.04})
axes[0].plot(LL_ldc.index, LL_ldc)
axes[0].set_ylabel('Energy Not Served [MW]')
axes[0].legend(loc='upper right')
axes[1].plot(LL_ldc.index, compare)
axes[1].set_ylabel('Net energy surplus/deficit [MWh]')
plt.show()

# Plot soft-linking statistics
dl.plot_convergence(LostLoad, ShedLoad, Curtailment, Error, iterations, figsize=(8, 12),
                 save_path='E:/OneDrive/KU Leuven/PhD/Thesis/LaTex/chapters/application3/image/BD_SL_Summary_' +
                           case_study + '.png')

# Plot rugplot
data_heatmap = pd.DataFrame()
for i in range(5):
    data_heatmap.loc[:, 'ENS_' + str(i)] = LostLoad.iloc[:, i] + ShedLoad.iloc[:, i]
    data_heatmap.loc[:, 'Curtailment_' + str(i)] = Curtailment.iloc[:, i]
dl.plot_rug(data_heatmap, cmap='Reds', fig_title='ENS - Curtailment comparison')

# Plot storage
dl.plot_storage(es_outputs, max_loops, td_df, inputs, results, results_mts=results_mts,
                save_path='E:/OneDrive/KU Leuven/PhD/Thesis/LaTex/chapters/application3/image/Seasonal_DHN.png')

#

dl.plot_capacity_energy_mix(inputs, results, es_outputs, ShedLoad, LostLoad, max_loops,
                            save_path='E:/OneDrive/KU Leuven/PhD/Thesis/LaTex/chapters/application3/image/Capacity_Energy_Mix.png',
                            )
# Plots
import pandas as pd

rng = pd.date_range('2015-01-01', '2015-12-31-23:00', freq='H')
# Generate country-specific plots
ds.plot_zone(inputs[4], results[4], rng=rng)
