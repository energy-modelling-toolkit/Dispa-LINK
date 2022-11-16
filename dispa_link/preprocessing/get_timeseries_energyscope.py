"""
This script generates the country time series for Dispa-SET
Input : EnergyScope database
Output : Database/Heat_demand/##/... .csv

@authors:
                Matija Pavičević, KU Leuven
                Paolo Thiran, UCLouvain
@contributors:
                Damon Coates, UCLouvain
                Guillaume Percy, UCLouvain
@supervision:
                Sylvain Quoilin, KU Leuven, ULiege
"""
from __future__ import division

import pandas as pd

from ..search import *
from ..common import *
from ..constants import *


def get_electricity_demand(es_outputs, td_df, drange, countries=['ES'], write_csv=True, file_name='Load'):
    """
    Compute electricity demand and convert it to dispaset readable format, i.e. csv time series
    :param es_outputs:  EnergyScope outputs
    :param td_df:       Typical day dataframe
    :param drange:      Date range
    :param countries:   Countries to apply the mapping function on
    :param write_csv:   Bool for creating csv file True/False
    :param file_name:   Name of the csv file
    :return:            Electricity demand
    """

    # Convert TD to hours
    electricity_layers = assign_td(es_outputs['electricity_layers'], td_df) * 1000
    demand_cols = ['ELEC_EXPORT', 'TRAMWAY_TROLLEY', 'TRAIN_PUB', 'TRAIN_FREIGHT', 'TRUCK_ELEC',
                   'BIO_HYDROLYSIS', 'PYROLYSIS_TO_LFO', 'PYROLYSIS_TO_FUELS', 'ATM_CCS', 'INDUSTRY_CCS',
                   'SYN_METHANOLATION', 'BIOMASS_TO_METHANOL', 'HABER_BOSCH', 'OIL_TO_HVC', 'GAS_TO_HVC',
                   'BIOMASS_TO_HVC', 'END_USE']
    grid_losses = grid_losses_list[countries.index('ES')]
    # Create final dataframe
    electricity = pd.DataFrame(-electricity_layers.loc[:, demand_cols].sum(axis=1).values * (1 + grid_losses),
                               index=drange, columns=countries)
    if write_csv:
        write_csv_files(file_name, electricity, 'TotalLoadValue', index=True, write_csv=True)
    return electricity


def get_heat_demand(es_outputs, td_df, drange, countries=None, write_csv=True, file_name='HeatDemand',
                    dispaset_version='2.5'):
    """
    Mapping function for heat demands
    :param es_outputs:  Energyscope outputs
    :param td_df:       Typical days dataframe
    :param countries:   Zones to be selected for mapping
    :param write_csv:   Bool that triggers writing csv files True/False
    :param file_name:   Name of the csv file
    :return:            Heat Demand timeseries
    """

    for country in countries:
        # %% assign typical days and convert to hourly timeseries
        ind_heat_es_input = assign_td(es_outputs['high_t_Layers'], td_df) * 1000  # GW to MW
        dhn_heat_es_input = assign_td(es_outputs['low_t_dhn_Layers'], td_df) * 1000  # GW to MW
        decen_heat_es_input = assign_td(es_outputs['low_t_decen_Layers'], td_df) * 1000  # GW to MW

        ind_heat_es = -ind_heat_es_input.loc[:, 'END_USE']
        dhn_heat_es = -dhn_heat_es_input.loc[:, 'END_USE']
        decen_heat_es = -decen_heat_es_input.loc[:, 'END_USE']

        # %% create a dataframe
        heat_es_input = pd.DataFrame()
        heat_es_input.loc[:, country + '_IND'] = ind_heat_es
        heat_es_input.loc[:, country + '_DHN'] = dhn_heat_es
        heat_es_input.loc[:, country + '_DEC'] = decen_heat_es
        heat_es_input.set_index(drange, inplace=True)

    # %% export to csv file
    if dispaset_version == '2.5':
        if write_csv:
            write_csv_files(file_name, heat_es_input, 'HeatDemand', index=True, write_csv=True, heating=True)

    return heat_es_input


def get_x_demand(X_layer, td_df, drange, write_csv=True, file_name='H2_demand', dispaset_version='2.5', columns=[],
                 layer_name=''):
    """
    Get h2 demand from ES and convert it into DS demand timeseries
    :param X_layer:    H2 inputs layer
    :param td_df:       typical day assignment
    :param write_csv:   write csv files
    :return:            h2 demand timeseries
    """
    X_layer = clean_blanks(X_layer, idx=False)
    X_layer = X_layer.dropna(axis=1, how='all')
    X_layer = X_layer.loc[:, columns]
    # computing consumption of H2
    # TODO automatise name zone assignment
    x_td = pd.DataFrame(X_layer.sum(axis=1), columns=[layer_name])
    x_ts = assign_td(x_td, td_df) * 1000  # Convert to MW
    x_ts.set_index(drange, inplace=True)
    if dispaset_version == '2.5':
        x_max_demand = pd.DataFrame(x_ts.max(), columns=['Capacity'])
    if write_csv:
        if dispaset_version == '2.5':
            write_csv_files(file_name, x_ts, 'H2_demand', index=True, write_csv=True)
            write_csv_files('PtLCapacities', x_max_demand, 'H2_demand', index=True, write_csv=True)
    return x_ts


def get_outage_factors(config_es, es_outputs, local_res, td_df, drange, write_csv=True):
    """
    Assign outage factors for technologies that generate more than available
    :param config_es:   EnergyScope config file
    :param es_outputs:  Energy scope outputs
    :param local_res:   Resources to compute outages
    :param td_df:       Typical day dataframe
    :return:            Outage factors
    """
    outage_factors = compute_outage_factor(config_es, es_outputs['assets'], local_res[0])
    for r in local_res[1:]:
        outage_factors = outage_factors.merge(compute_outage_factor(config_es, es_outputs['assets'], r),
                                              left_index=True, right_index=True)

    outage_factors_yr = td_df.loc[:, ['TD', 'hour']]
    outage_factors_yr = outage_factors_yr.merge(outage_factors, left_on=['TD', 'hour'], right_index=True).sort_index()
    outage_factors_yr.drop(columns=['TD', 'hour'], inplace=True)
    outage_factors_yr.rename(columns=lambda x: 'ES_' + x, inplace=True)
    outage_factors_yr.set_index(drange, inplace=True)
    if write_csv:
        write_csv_files('OutageFactor', outage_factors_yr, 'OutageFactor', index=True, write_csv=True)
    return outage_factors_yr


def get_soc(es_outputs, config_es, drange, sto_size_min=0.01, countries=None, write_csv=True,
            file_name='ReservoirLevels'):
    """
    Compute the state of the charge of storage technologies
    :param es_outputs:      EnergyScope outputs
    :param config_es:       EnergyScope config file
    :param drange:          Date range
    :param sto_size_min:    Minimum storage size to be considered
    :param countries:       Countries to iterate over
    :param write_csv:       Bool for writing csv files True/False
    :param file_name:       Name of the csv file
    :return:                State of the charge
    """

    # TODO: make generic for any country
    sto_size = es_outputs['assets'].loc[config_es['all_data']['Storage_eff_in'].index, 'f']
    sto_size = sto_size[sto_size >= sto_size_min]
    soc = es_outputs['energy_stored'].loc[:, sto_size.index] / sto_size
    soc.rename(columns=lambda x: 'ES_' + x, inplace=True)
    soc.set_index(drange, inplace=True)

    if write_csv:
        write_csv_files(file_name, soc, 'ReservoirLevels', index=True, write_csv=True)
    return soc


def get_availability_factors(es_outputs, drange, countries=['ES'], write_csv=True, file_name_af='AvailabilityFactors',
                             file_name_sif='ScaledInFlows'):
    """
    Get availability factors from Energy Scope and covert them to Dispa-SET readable format
    :param es_outputs:      EnergyScope outputs
    :param config_es:       EnergyScope config file
    :param drange:          Date range
    :param countries:       Countries to iterate over
    :param write_csv:       Bool for writing csv files True/False
    :param file_name_af:    Name of the availability factor csv file
    :param file_name_sif:   Name of the scaled inflows csv file
    :return:                RES time-series
    """

    # %% Create data structures
    res_timeseries = {}
    inflow_timeseries = {}

    for country in countries:
        # %% Fix input files
        es_outputs['timeseries'].set_index(drange, inplace=True)
        af_es_df = es_outputs['timeseries'].loc[:, ['PV', 'Wind_onshore', 'Wind_offshore', 'Hydro_river']]

        # %% Compute availability factors
        availability_factors_ds = []
        for i in af_es_df:
            if i in mapping['ES']['TECH']:
                availability_factors_ds.append(mapping['ES']['TECH'][i])
        availability_factors_ds_df = af_es_df.set_axis(availability_factors_ds, axis=1, inplace=False)
        for i in availability_factors_ds:
            availability_factors_ds_df.loc[availability_factors_ds_df[i] < 0, i] = 0
            availability_factors_ds_df.loc[availability_factors_ds_df[i] > 1, i] = 1
        res_timeseries[country] = availability_factors_ds_df

        # %% Compute scaled inflows, if present
        try:
            inflows_ds = []
            inflows_es_df = es_outputs['timeseries'].loc[:, ['Hydro_dam']]
            for i in inflows_es_df:
                if i in mapping['ES']['TECH']:
                    inflows_ds.append(mapping['ES']['TECH'][i])
            inflow_timeseries[country] = inflows_es_df.set_axis(inflows_ds, axis=1)
        except:
            logging.error('Hydro_dam time-series not present in ES')

        # %% Export to csv
        if write_csv:
            write_csv_files(file_name_af, res_timeseries[country], 'AvailabilityFactors', index=True, write_csv=True,
                            country=country)
            if inflow_timeseries:
                write_csv_files(file_name_sif, inflow_timeseries[country], 'ScaledInFlows', index=True, write_csv=True,
                                country=country, inflows=True)

    return res_timeseries


def get_ev_demand(es_outputs, td_df, ds_inputs, drange, countries=['ES'], write_csv=True, file_name='EV_Load'):
    """
    Compute electricity demand for electric vehicles and convert it to dispaset readable format, i.e. csv time series
    :param es_outputs:  EnergyScope outputs
    :param td_df:       Typical day dataframe
    :param drange:      Date range
    :param countries:   Countries to apply the mapping function on
    :param write_csv:   Bool for creating csv file True/False
    :param file_name:   Name of the csv file
    :return:            ev_demand
    """
    electricity_layers = assign_td(es_outputs['electricity_layers'], td_df) * 1000
    demand_cols = ['CAR_PHEV', 'CAR_BEV']
    ev_cols = ['ES_PHEV_BATT', 'ES_BEV_BATT']
    ev_scaled_demand = pd.DataFrame()
    for ev in ev_cols:
        if ev == 'ES_PHEV_BATT':
            search = 'CAR_PHEV'
        else:
            search = 'CAR_BEV'
        if not ds_inputs[0][ds_inputs[0]['Unit'] == ev].empty:
            ev_techs = ds_inputs[0].loc[ds_inputs[0]['Unit'].isin([ev]), 'PowerCapacity']
            ev_scaled_demand[ev] = -electricity_layers.loc[:, search].values / ev_techs.values
        else:
            ev_scaled_demand[ev] = -electricity_layers.loc[:, search]

    ev_demand = pd.DataFrame(ev_scaled_demand.values, index=drange, columns=['ES_PHEV_BATT', 'ES_BEV_BATT'])

    if write_csv:
        write_csv_files(file_name, ev_demand, 'TotalLoadValue', index=True, write_csv=True)

    return ev_demand


def merge_timeseries_x(ds_inputs, df, td_df, drange, dispaset_version, i):
    """
    Merge all the supply demand time-series into a single csv file
    :param ds_inputs:           ds_inputs dictionary
    :param df:                  Energy Scope output layers
    :param td_df:               Typical day to hourly dataframe
    :param drange:              Date range
    :param dispaset_version:    Dispaset version
    :return:                    populated ds_inputs dictionary
    """
    # Assign fixed demands in Sector X
    ds_inputs['XFixDemand'][i] = - cocncat_ts(ds_inputs, df, td_df, drange, dispaset_version, i,
                                              var_name='XFixDemand',
                                              # layers=['h2', 'ammonia', 'gas', 'ind', 'dhn', 'dec', 'wood', 'lfo', 'coal', 'waste'])
                                              layers=['h2', 'ammonia', 'ind', 'dhn', 'dec', 'wood', 'lfo', 'coal',
                                                      'waste'])
    # Assign Variable Demands in Sector X
    ds_inputs['XVarDemand'][i] = - cocncat_ts(ds_inputs, df, td_df, drange, dispaset_version, i,
                                              # var_name='XVarDemand', layers=['gas', 'ind'])
                                              var_name='XVarDemand', layers=['ind'])
    # Assign fixed supply in Sector X
    ds_inputs['XFixSupply'][i] = cocncat_ts(ds_inputs, df, td_df, drange, dispaset_version, i,
                                            # var_name='XFixSupply', layers=['h2', 'ammonia', 'gas', 'dhn', 'lfo'])
                                            var_name='XFixSupply', layers=['h2', 'ammonia', 'ind', 'dhn', 'dec', 'lfo'])
    # Assign variable supply in Sector X
    ds_inputs['XVarSupply'][i] = cocncat_ts(ds_inputs, df, td_df, drange, dispaset_version, i,
                                            var_name='XVarSupply',
                                            # layers=['h2', 'ammonia', 'gas', 'wood', 'lfo', 'coal', 'waste'])
                                            layers=['h2', 'ammonia', 'ind', 'dhn', 'dec', 'wood', 'lfo', 'coal', 'waste'])
    return ds_inputs


def cocncat_ts(ds_inputs, df, td_df, drange, dispaset_version, i, var_name='XVarSupply',
               layers=['h2', 'ammonia', 'gas', 'ind', 'dhn', 'dec', 'wood', 'lfo', 'coal', 'waste']):
    """

    :param ds_inputs:           ds_inputs dictionary
    :param df:                  Energy Scope output layers
    :param td_df:               Typical day to hourly dataframe
    :param drange:              Date range
    :param dispaset_version:    Dispaset version
    :param i:                   Iteration
    :param var_name:            Variable name to be assigned XVarSupply, XFixDemand ....
    :param layers:              Layers to be represented as a boundary sector
    :return:
    """
    mpng = {'layer': {'h2': 'h2_layer',
                      'ammonia': 'ammonia_layer',
                      'gas': 'gas_layer',
                      'ind': 'high_t_Layers',
                      'dhn': 'low_t_dhn_Layers',
                      'dec': 'low_t_decen_Layers',
                      'wood': 'wood_layer',
                      'lfo': 'lfo_layer',
                      'coal': 'coal_layer',
                      'waste': 'waste_layer'},
            'layer_name': {'h2': 'ES_H2',
                           'ammonia': 'ES_AMO',
                           'gas': 'ES_GAS',
                           'ind': 'ES_IND',
                           'dhn': 'ES_DHN',
                           'dec': 'ES_DEC',
                           'wood': 'ES_BIO',
                           'lfo': 'ES_OIL',
                           'coal': 'ES_HRD',
                           'waste': 'ES_WST'},
            'lookup': {'XVarSupply': '_var_sup',
                       'XVarDemand': '_var_dem',
                       'XFixSupply': '_fix_sup',
                       'XFixDemand': '_fix_dem'}
            }

    ds_inputs[var_name][i] = pd.DataFrame()
    for l in layers:
        ds_inputs[var_name][i] = pd.concat([ds_inputs[var_name][i],
                                            get_x_demand(df[mpng['layer'][l]], td_df, drange,
                                                         dispaset_version=dispaset_version,
                                                         columns=common['ES'][l + mpng['lookup'][var_name]],
                                                         layer_name=mpng['layer_name'][l])], axis=1)

    return ds_inputs[var_name][i]
