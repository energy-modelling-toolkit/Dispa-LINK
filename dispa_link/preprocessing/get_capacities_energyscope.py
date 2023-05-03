import logging
import sys

import numpy as np
import pandas as pd

from ..constants import mapping, n_TD  # line to import the dictionary
from ..dispa_link_functions import define_units, assign_parameters, assign_gas_units, assign_parameters_by_index, \
    assign_zone, assign_typical_values
from ..preprocessing.get_timeseries_energyscope import get_x_demand
from ..search import sto_dhn, write_csv_files, column_names_bs, column_names  # line to import the dictionary


def get_capacities_from_es(es_outputs, typical_units, td_df, zone=None, write_csv=True, file_name='PowerPlants',
                           technology_threshold=0, storage_threshold=0.5, t_env=273.15 + 35, t_dhn=90, t_ind=120,
                           dispaset_version='2.5', config_link=None, ds_inputs=None, i=0):
    """
        Data needed for the Power Plants in DISPA-SET (ES means from ES): 
        - Unit Name
        - Capacity : Power Capacity [MW]    ==>     ES + Up to US [Repartitioning through Typical_Units.csv]
        - Nunits                            ==>     ES Capacity Installed + [Repartitioning through Typical_Units.csv]
        - Year : Comissionning Year         ==>     For each year new powerplant database is needed
        - Technology                        ==>     ES + Dico
        - Fuel : Primary Fuel               ==>     ES + Dico
        - Fuel Prices                       ==>     Set them as constant
        -------- Technology and Fuel in ES correspond to 1 technology in DISPA-SET -------- 
        - Zone :                            ==>     To be implemented based on historical data
        - Efficiency [%]                    ==>     ES + Typical_units.csv
        - Efficiency at min load [%]        ==>     Typical_units.csv
        - CO2 Intensity [TCO2/MWh]          ==>     ES + Typical_units.csv
        - Min Load [%]                      ==>     Typical_units.csv
        - Ramp up rate [%/min]              ==>     Typical_units.csv
        - Ramp down rate [%/min]            ==>     Typical_units.csv
        - Start-up time[h]                  ==>     Typical_units.csv
        - MinUpTime [h]                     ==>     Typical_units.csv
        - Min down Time [h]                 ==>     Typical_units.csv
        - No Load Cost [EUR/h]              ==>     Typical_units.csv
        - Start-up cost [EUR]               ==>     Typical_units.csv
        - Ramping cost [EUR/MW]             ==>     Typical_units.csv
        - Presence of CHP [y/n] & Type      ==>     ES + Typical_units.csv
        - CHPPowerToHeat                    ==>     ES + Typical_units.csv
        - CHPPowerLossFactor                ==>     Typical_units.csv
        - CHPMaxHeat                        ==>     if needed from Typical_units.csv
    
        column_names = [# Generic
                        'Unit', 'PowerCapacity', 'Nunits', 'Zone', 'Zone_th', 'Zone_H2', 'Technology', 'Fuel', 
                        # Technology specific
                        'Efficiency', 'MinUpTime', 'MinDownTime', 'RampUpRate', 'RampDownRate', 'StartUpCost_pu', 
                        'NoLoadCost_pu', 'RampingCost', 'PartLoadMin', 'MinEfficiency', 'StartUpTime', 'CO2Intensity',
                        'WaterWithdrawal', 'WaterConsumption',
                        # CHP related
                        'CHPType', 'CHPPowerToHeat', 'CHPPowerLossFactor', 'CHPMaxHeat',
                        # P2HT related
                        'COP', 'Tnominal', 'coef_COP_a', 'coef_COP_b', 
                        # Storage related
                        'STOCapacity', 'STOSelfDischarge', 'STOMaxChargingPower', 'STOChargingEfficiency']
    """

    # %% Clean data
    es_outputs['assets'] = es_outputs['assets'].groupby(es_outputs['assets'].index).mean()

    # %% Get GWP_op data, this will be used to compute CO2Intensity of different technologies inside DS
    es_outputs['GWP_op'].index = es_outputs['GWP_op'].index.map(mapping['ES']['RESOURCE'])

    ###############################################
    # ---- Do the mapping between ES and DS ----- #
    ###############################################

    power_plants = define_units(names=es_outputs['assets'].index)
    # Fill in the capacity value at Power Capacity column
    power_plants = assign_parameters(power_plants, es_outputs['assets']['f'], 'PowerCapacity')
    # Watch out for STO_TECH /!\ - PowerCapacity in DS is MW, where f is in GW/GWh
    # Here everything is in GW/GWh

    # Fill in the column Technology, Fuel according to the mapping Dictionary defined here above
    power_plants = assign_parameters(power_plants, power_plants.index.to_series().map(mapping['ES']['TECH']),
                                     'Technology')
    power_plants = assign_parameters(power_plants, power_plants.index.to_series().map(mapping['ES']['FUEL']), 'Fuel')

    # the column Sort is added to do some conditional changes for CHP and STO units
    power_plants = assign_parameters(power_plants, power_plants.index.to_series().map(mapping['ES']['SORT']), 'Sort')

    # Get rid of technology that do not have a Sort category + HeatSlack + Thermal Storage
    index_to_drop = power_plants[
        (power_plants['Sort'].isna()) | (power_plants['Sort'] == 'HeatSlack') | (power_plants['Sort'] == 'THMS') |
        (power_plants['Sort'] == '')].index
    if len(power_plants[power_plants['Sort'].isna()].index.tolist()) != 0:
        logging.warning(
            'Several techs are dropped as they are not referenced in the Dictionary : Sort. Here is the list : ' +
            str(power_plants[power_plants['Sort'].isna()].index.tolist()))
    if len(power_plants[power_plants['Sort'] == 'HeatSlack']) != 0:
        logging.warning('Several techs are dropped as they become HeatSlack in DS. Here is the list : ' +
                        str(power_plants[power_plants['Sort'] == 'HeatSlack'].index.tolist()))

    # Keep the original data just in case
    original_units = power_plants.copy()
    # Assign more technologies to gas units based on occurance in real life
    power_plants = assign_gas_units(power_plants, comc=4279.6, gt=1550.7, stur=0,
                                    source_name='CCGT', source_fuel='GAS',
                                    gt_name='OCGT', comc_name='CCGT', stur_name='STUR', x=False)
    power_plants.drop(index_to_drop, inplace=True)

    # Getting all CHP/P2HT/ELEC/STO TECH present in the ES implementation
    chp_tech = list(power_plants.loc[power_plants['Sort'] == 'CHP'].index)
    p2ht_tech = list(power_plants.loc[power_plants['Sort'] == 'P2HT'].index)
    heat_tech = list(power_plants.loc[power_plants['Sort'] == 'HEAT'].index)
    electricity_tech = list(power_plants.loc[power_plants['Sort'] == 'ELEC'].index)
    storage_tech = list(power_plants.loc[power_plants['Sort'] == 'STO'].index)
    p2gs_tech = list(power_plants.loc[power_plants['Sort'] == 'P2GS'].index)
    h2_sto_tech = list(power_plants.loc[power_plants['Sort'] == 'P2GS_STO'].index)
    thms = list(original_units.loc[original_units['Technology'] == 'THMS'].index)
    heat_tech_all = p2ht_tech + chp_tech + heat_tech

    # Variable used later in CHP and P2HT units regarding THMS of DHN units
    tech_sto_daily = 'TS_DHN_DAILY'
    sto_daily_cap = float(original_units.at[tech_sto_daily, 'PowerCapacity'])
    sto_daily_losses = es_outputs['storage_characteristics'].at[tech_sto_daily, 'storage_losses']
    tech_sto_seasonal = 'TS_DHN_SEASONAL'
    sto_seasonal_cap = float(original_units.at[tech_sto_seasonal, 'PowerCapacity'])
    sto_seasonal_losses = es_outputs['storage_characteristics'].at[tech_sto_seasonal, 'storage_losses']

    boundary_sector_inputs = pd.DataFrame(columns=['Sector', 'STOCapacity', 'STOSelfDischarge', 'STOMinSOC',
                                                   'MaxFlexDemand', 'MaxFlexSupply'])

    # %% --------------- Changes only for ELEC Units  --------------- TO CHECK
    #      - Efficiency
    for tech in electricity_tech:
        tech_resource = mapping['ES']['FUEL_ES'][tech]  # gets the correct column electricity to look up per CHP tech
        try:
            if tech == 'OCGT_GAS':
                efficiency = typical_units.loc[(typical_units['Technology'] == 'GTUR') &
                                               (typical_units['Fuel'] == 'GAS'), 'Efficiency'].values[0]
            elif tech == 'CCGT_GAS':
                efficiency = typical_units.loc[(typical_units['Technology'] == 'COMC') &
                                               (typical_units['Fuel'] == 'GAS'), 'Efficiency'].values[0]
            elif tech == 'STUR_GAS':
                efficiency = typical_units.loc[(typical_units['Technology'] == 'STUR') &
                                               (typical_units['Fuel'] == 'GAS'), 'Efficiency'].values[0]
            # If the TECH is ELEC , Efficiency is simply abs(ELECTRICITY/RESSOURCES)
            else:
                efficiency = abs(es_outputs['layers_in_out'].at[tech, 'ELECTRICITY'] /
                                 es_outputs['layers_in_out'].at[tech, tech_resource])
            power_plants = assign_parameters_by_index(power_plants, tech, ['Efficiency'], [efficiency])
        except:
            logging.warning(' Technology ' + tech + ' has not been found in layers_in_out')

    # %% --------------- Changes only for P2GS Units  --------------- TO CHECK
    #      - Efficiency
    #       -
    #       Then comes the associated storage
    #       -
    for tech in p2gs_tech:
        # gets the correct column electricity to look up per CHP tech
        tech_resource = mapping['ES']['FUEL_ES'][tech]
        try:
            # If the TECH is ELEC , Efficiency is simply abs(ELECTRICITY/RESSOURCES) - TO CHECK -------------------
            efficiency = abs(es_outputs['layers_in_out'].at[tech, 'H2'] /
                             es_outputs['layers_in_out'].at[tech, tech_resource])
            if dispaset_version == '2.5':
                power_plants = assign_parameters_by_index(power_plants, tech, ['Efficiency'], [efficiency])
            elif dispaset_version == '2.5_BS':
                # FIXME: check if ELY and FC are properly mapped
                efficiency_high_temp = es_outputs['layers_in_out'].at[tech, 'HEAT_HIGH_T'] / \
                                       es_outputs['layers_in_out'].at[tech, tech_resource]
                efficiency_dhn = es_outputs['layers_in_out'].at[tech, 'HEAT_LOW_T_DHN'] / \
                                 es_outputs['layers_in_out'].at[tech, tech_resource]
                power_plants = assign_parameters_by_index(power_plants, tech,
                                                          ['Efficiency', 'ChargingEfficiencySector1',
                                                           'Sector2', 'ChargingEfficiencySector2',
                                                           'Sector3', 'ChargingEfficiencySector3'],
                                                          [1, efficiency, 'ES_IND', -efficiency_high_temp,
                                                           'ES_DHN', -efficiency_dhn])
            else:
                logging.error('Wrong Dispa-SET version selected')
                sys.exit(1)
        except:
            logging.warning(' Technology ' + tech + ' has not been found in layers_in_out')

        try:
            # Associate the right P2GS Storage ith the P2GS production unit - TO DO  ----------------------------
            p2gs_sto = mapping['ES']['P2GS_STORAGE'][tech]
            # OK
        except:
            logging.warning(' Associated P2GS storage ' + p2gs_sto + 'is not referenced in the dictionary')

        try:
            # For other Tech ' f' in ES = PowerCapacity, whereas for STO_TECH ' f' = STOCapacity
            storage_capacity = power_plants.at[p2gs_sto, 'PowerCapacity']
            storage_self_discharge = es_outputs['storage_characteristics'].at[p2gs_sto, 'storage_losses']
            storage_charging_efficiency = es_outputs['storage_eff_in'].at[p2gs_sto, 'H2']
            # GW to MW
            storage_max_charge_power = float(storage_capacity) / \
                                       es_outputs['storage_characteristics'].at[p2gs_sto, 'storage_charge_time'] * 1000
            if dispaset_version == '2.5':
                power_plants = assign_parameters_by_index(power_plants, tech,
                                                          ['STOCapacity', 'STOSelfDischarge', 'STOMaxChargingPower',
                                                           'STOChargingEfficiency'],
                                                          [storage_capacity, storage_self_discharge,
                                                           storage_max_charge_power, storage_charging_efficiency])
                # power_plants.loc[
                #     power_plants.index == tech, ['STOCapacity', 'STOSelfDischarge', 'STOMaxChargingPower',
                #                                  'STOChargingEfficiency']] = [storage_capacity, storage_self_discharge,
                #                                                               storage_max_charge_power,
                #                                                               storage_charging_efficiency]
            elif dispaset_version == '2.5_BS':
                # Adjust P2GS unit to boundary sector conditions
                # FIXME: i need to be generic so that it is also possible to destinguish between ELY and FC
                storage_max_charge_power = power_plants.loc[power_plants.index == tech, 'PowerCapacity']
                power_plants = assign_parameters_by_index(power_plants, tech, ['STOMaxChargingPower', 'PowerCapacity'],
                                                          [storage_max_charge_power, 0])
        except:
            logging.warning(' Technology ' + p2gs_sto + ' has not been found in STO_eff_out/eff_in/_characteristics')

        if dispaset_version == '2.5':
            if zone is None:
                power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_h2'], ['ES_H2'])
            else:
                power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_h2'], [zone + '_H2'])

        elif dispaset_version == '2.5_BS':
            h2_ts = get_x_demand(es_outputs['h2_layer'], td_df, config_link['DateRange'], write_csv=False,
                                 dispaset_version='2.5_BS')
            for z in h2_ts.columns:
                boundary_sector_inputs = assign_parameters_by_index(boundary_sector_inputs, z,
                                                                    ['MaxFlexDemand', 'Sector', 'STOCapacity',
                                                                     'STOSelfDischarge'],
                                                                    [h2_ts[z].max(), z, storage_capacity,
                                                                     storage_self_discharge])
            if zone is None:
                power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], ['ES_H2'])
            else:
                power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone + '_H2'])

        else:
            logging.error('Wrong Dispa-SET version selected')
            sys.exit(1)

    # %% --------------- Changes only for CHP Units  --------------- TO CHECK
    #      - Efficiency
    #      - PowerToTheatRatio
    #      - CHPType

    # for each CHP_tech, we will extract the PowerToHeat Ratio and add it to the PowerPlants dataFrame
    for tech in chp_tech:
        tech_resource = mapping['ES']['FUEL_ES'][tech]  # gets the correct column resources to look up per CHP tech
        tech_heat = mapping['ES']['CHP_HEAT'][tech]  # gets the correct column heat to look up per CHP tech
        try:
            power_to_heat_ratio = abs(es_outputs['layers_in_out'].at[tech, 'ELECTRICITY'] /
                                      es_outputs['layers_in_out'].at[tech, tech_heat])
            # If the TECH is CHP  , Efficiency is simply abs(ELECTRICITY/RESSOURCES)
            efficiency = abs(es_outputs['layers_in_out'].at[tech, 'ELECTRICITY'] /
                             es_outputs['layers_in_out'].at[tech, tech_resource])

            # Power Capacity of the plant is defined in ES regarding Heat. But in DS, it is defined regarding Elec.
            # Hence PowerCap_DS = PowerCap_ES*phi ; where phi is the PowerToHeat Ratio
            capacity = float(power_plants.at[tech, 'PowerCapacity']) * power_to_heat_ratio

            # TODO: Decide how to assign extraction turbines maybe with temperature levels in DH networks
            # CHP units in ES have a constant PowerToHeatRatio which makes them 'back-pressure' units by default - IMPROVE
            beta = 0
            if power_plants.loc[tech, 'Technology'] in ['STUR', 'COMC']:
                if tech[0:4] in ['DEC_']:
                    chp_type = 'back-pressure'
                else:
                    chp_type = 'Extraction'
                    if tech[0:4] in ['DHN_']:
                        t_extraction = 273.15 + t_dhn
                    else:
                        t_extraction = 273.15 + t_ind
                    beta = (t_extraction - t_env) / t_env
            else:
                chp_type = 'back-pressure'

            power_plants = assign_parameters_by_index(power_plants, tech,
                                                      ['PowerCapacity', 'CHPPowerToHeat', 'Efficiency',
                                                       'CHPType', 'CHPPowerLossFactor'],
                                                      [capacity, power_to_heat_ratio, efficiency, chp_type, beta])

        except:
            logging.warning(' Technology ' + tech + ' has not been found in layers_in_out')

    # %% --------------- Changes only for P2HT Units  --------------- TO CHECK
    #      - Efficiency - it's just 1
    #      - COP

    # for each P2HT_tech, we will extract the COP Ratio and add it to the PowerPlants dataFrame
    for tech in p2ht_tech:
        tech_resource = mapping['ES']['FUEL_ES'][tech]
        # gets the correct column heat to look up per CHP tech
        tech_heat = mapping['ES']['P2HT_HEAT'][tech]

        try:
            cop = abs(
                es_outputs['layers_in_out'].at[tech, tech_heat] / es_outputs['layers_in_out'].at[tech, 'ELECTRICITY'])
        except:
            logging.warning(' Technology P2HT' + tech + ' has not been found in layers_in_out')

        # Efficiency = layers_in_out.at[tech,'ELECTRICITY']/layers_in_out.at[tech,tech_ressource]
        # Power Capacity of the plant is defined in ES regarding Heat.
        # But in DS, it is defined regarding Elec. Hence PowerCap_DS = PowerCap_ES/COP
        capacity = float(power_plants.at[tech, 'PowerCapacity']) / cop

        power_plants = assign_parameters_by_index(power_plants, tech, ['PowerCapacity', 'Efficiency', 'COP'],
                                                  [capacity, 1.0, cop])

    # %% --------------- Changes only for Heat only Units  --------------- TO CHECK
    #      - Efficiency

    for tech in heat_tech:
        tech_resource = mapping['ES']['FUEL_ES'][tech]
        heat_type = mapping['ES']['HEAT_ONLY_HEAT'][tech]
        # gets the correct column electricity to look up per CHP tech
        try:
            # If the TECH is HEAT , Efficiency is simply abs(HEAT/RESOURCES)
            efficiency = abs(
                es_outputs['layers_in_out'].at[tech, heat_type] / es_outputs['layers_in_out'].at[tech, tech_resource])
        except:
            efficiency = np.nan
            logging.warning(' Technology ' + tech + ' has not been found in layers_in_out')
        power_plants = assign_parameters_by_index(power_plants, tech, ['Efficiency'], efficiency)

    # %% --------------------------------THERMAL STORAGE FOR P2HT, HEAT and CHP UNITS ----------------------------------
    # tech_sto can be of 2 cases :
    #    1) either the CHP tech is DEC_TECH, then it has its own personal storage named TS_DEC_TECH
    #    2) or the CHP tech is DHN_TECH. these tech are associated with TS_DHN_DAILY and TS_DHN_SEASONAL;

    # get the dhn_daily and dhn_seasonal before the for loop
    # the list used CHP_tech could be brought to a smaller number reducing computation time - through the use of
    # tech.startswith('DHN_') ? - TO DO
    sto_dhn_daily = sto_dhn(heat_tech, 'DAILY', n_TD, es_outputs['assets'], es_outputs['low_t_dhn_Layers'], td_df)
    sto_dhn_seasonal = sto_dhn(heat_tech, 'SEASONAL', n_TD, es_outputs['assets'], es_outputs['low_t_dhn_Layers'], td_df)
    tot_sto_dhn_daily = sto_dhn_daily.sum()
    tot_sto_dhn_seasonal = sto_dhn_seasonal.sum()

    for tech in heat_tech_all:
        try:
            if tech.startswith('DEC_'):
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('DEC', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])

            elif tech.startswith('DHN_'):
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('DHN', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])

            elif tech.startswith('IND_'):  # If the unit is IND - so making HIGH TEMPERATURE - no Thermal Storage
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('IND', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])
        except:
            logging.warning('Technology ' + tech + ' doesnt have a thermal storage option in ES')

    # %% -------------- STO UNITS --------------------- ==> Only units storing ELECTRICITY - TO CHECK
    #      - STOCapacity
    #      - STOSelfDischarge
    #      - PowerCapacity
    #      - STOMaxChargingPower
    #      - STOChargingEfficiency
    #      - Efficiency
    #      - TO CHECK/FINISH

    for tech in storage_tech:

        try:
            if tech.startswith('TS_DEC_'):
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('DEC', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])
                if tech.startswith('TS_DEC_'):
                    storage_charging_efficiency = es_outputs['storage_eff_in'].at[tech, 'HEAT_LOW_T_DECEN']
                    efficiency = es_outputs['storage_eff_out'].at[tech, 'HEAT_LOW_T_DECEN']

            elif tech.startswith('TS_DHN_'):
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('DHN', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])
                if tech.startswith('TS_DHN_'):
                    storage_charging_efficiency = es_outputs['storage_eff_in'].at[tech, 'HEAT_LOW_T_DHN']
                    efficiency = es_outputs['storage_eff_out'].at[tech, 'HEAT_LOW_T_DHN']

            elif tech.startswith('TS_HIGH_'):  # If the unit is IND - so making HIGH TEMPERATURE - no Thermal Storage
                # Regarding heat coupling - assign to different heat nodes depending on the type of heat produced
                zone_name = assign_zone('IND', zone)
                if dispaset_version == '2.5':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Zone_th'], [zone_name])
                elif dispaset_version == '2.5_BS':
                    power_plants = assign_parameters_by_index(power_plants, tech, ['Sector1'], [zone_name])
                if tech.startswith('TS_HIGH_'):
                    storage_charging_efficiency = es_outputs['storage_eff_in'].at[tech, 'HEAT_HIGH_T']
                    efficiency = es_outputs['storage_eff_out'].at[tech, 'HEAT_HIGH_T']
            else:
                storage_charging_efficiency = es_outputs['storage_eff_in'].at[tech, 'ELECTRICITY']
                efficiency = es_outputs['storage_eff_out'].at[tech, 'ELECTRICITY']

            # GW to MW is done further
            # For other Tech ' f' in ES = PowerCapacity,
            # whereas for STO_TECH ' f' = STOCapacity
            storage_capacity = power_plants.at[tech, 'PowerCapacity']
            # In ES, the units are [%/s] whereas in DS the units are [%/h]
            storage_self_discharge = es_outputs['storage_characteristics'].at[tech, 'storage_losses']
            # Characteristics of charging and discharging
            # PowerCapacity = Discharging Capacity for STO_TECH in DS #GW to MW is done further
            PowerCapacity = float(storage_capacity) / es_outputs['storage_characteristics'].at[
                tech, 'storage_discharge_time']
            storage_max_charge_power = float(storage_capacity) / es_outputs['storage_characteristics'].at[
                tech, 'storage_charge_time'] * 1000  # GW to MW

            power_plants = assign_parameters_by_index(power_plants, tech,
                                                      ['STOCapacity', 'STOSelfDischarge', 'PowerCapacity',
                                                       'STOMaxChargingPower', 'STOChargingEfficiency', 'Efficiency'],
                                                      [storage_capacity, storage_self_discharge, PowerCapacity,
                                                       storage_max_charge_power, storage_charging_efficiency,
                                                       efficiency]
                                                      )
            # power_plants.loc[
            #     power_plants.index == tech, ['STOCapacity', 'STOSelfDischarge', 'PowerCapacity', 'STOMaxChargingPower',
            #                                  'STOChargingEfficiency', 'Efficiency']] = [storage_capacity,
            #                                                                             storage_self_discharge,
            #                                                                             PowerCapacity,
            #                                                                             storage_max_charge_power,
            #                                                                             storage_charging_efficiency,
            #                                                                             efficiency]
        except:
            logging.warning('Technology ' + tech + 'has not been found in STO_eff_out/eff_in/_characteristics')

    # %% ------------ TYPICAL UNITS MAKING ----------
    # Part of the code where you fill in DATA coming from typical units

    technology_fuel_in_system = power_plants[['Technology', 'Fuel']].copy()
    technology_fuel_in_system = technology_fuel_in_system.drop_duplicates(subset=['Technology', 'Fuel'], keep='first')
    technology_fuel_in_system = technology_fuel_in_system.values.tolist()

    # Typical Units : run through Typical_Units with existing Technology_Fuel pairs in ES simulation

    # Characteristics is a list over which we need to iterate for typical Units
    # characteristics = ['MinUpTime', 'MinDownTime', 'RampUpRate', 'RampDownRate', 'StartUpCost_pu', 'NoLoadCost_pu',
    #                    'RampingCost', 'PartLoadMin', 'MinEfficiency', 'StartUpTime', 'CO2Intensity',
    #                    'CHPPowerLossFactor']

    # Get Indexes to iterate over them
    index_list = list(
        power_plants.loc[(power_plants['Sort'] != 'CHP') & (power_plants['Sort'] != 'P2GS')].index.values.tolist())
    index_chp_list = list(power_plants.loc[power_plants['Sort'] == 'CHP'].index.values.tolist())
    index_p2gs_list = list(power_plants.loc[power_plants['Sort'] == 'P2GS'].index.values.tolist())

    for index in index_list:
        if power_plants.loc[index, 'Fuel'] in list(es_outputs['GWP_op'].index):
            power_plants.loc[index, 'CO2Intensity'] = es_outputs['GWP_op'].loc[power_plants.loc[index, 'Fuel']] / \
                                                      power_plants.loc[index, 'Efficiency']

    # %% ------------------------------ For units consuming X and generating power -------------------------------------
    for index in power_plants.index:
        if power_plants.loc[index, 'Technology'] in ['COMCX', 'GTURX', 'ICENX', 'STURX']:
            for f in ['AMO', 'GAS', 'BIO', 'OIL', 'HRD', 'WST']:
                if power_plants.loc[index, 'Fuel'] == f:
                    try:
                        efficiency = - power_plants.loc[index, 'Efficiency']
                        power_plants = assign_parameters_by_index(power_plants, index,
                                                                  ['Efficiency', 'Sector1', 'EfficiencySector1'],
                                                                  [1, 'ES_' + f, efficiency])
                    except:
                        logging.warning(' Technology ' + index + ' has not been found in layers_in_out')


    # boundary_sector_inputs = pd.DataFrame(index=['ES_H2', 'ES_AMO', 'ES_GAS', 'ES_IND', 'ES_DHN', 'ES_OIL'])
    # for index in ['H2_STORAGE', 'GAS_STORAGE', 'AMMONIA_STORAGE', 'TS_HIGH_TEMP', 'TS_DHN_SEASONAL', 'LFO_STORAGE']:
    boundary_sector_inputs = pd.DataFrame(index=['ES_H2', 'ES_AMO', 'ES_IND', 'ES_DHN', 'ES_DEC', 'ES_OIL', 'ES_HRD', 'ES_WST', 'ES_BIO'])
    for index in ['H2_STORAGE', 'AMMONIA_STORAGE', 'TS_HIGH_TEMP', 'TS_DHN_SEASONAL', 'ES_OIL', 'ES_HRD', 'ES_WST', 'ES_BIO', 'ES_DEC']:
        if index in ['H2_STORAGE', 'GAS_STORAGE', 'AMMONIA_STORAGE', 'TS_HIGH_TEMP', 'TS_DHN_SEASONAL', 'LFO_STORAGE']:
            storage_capacity = original_units.loc[index, 'PowerCapacity'] * 1000
            storage_self_discharge = es_outputs['storage_characteristics'].loc[index, 'storage_losses']
        else:
            storage_capacity = np.nan
            storage_self_discharge = np.nan
        if index == 'H2_STORAGE':
            sector = 'ES_H2'
        elif index == 'GAS_STORAGE':
            sector = 'ES_GAS'
        elif index == 'AMMONIA_STORAGE':
            sector = 'ES_AMO'
        elif index == 'TS_HIGH_TEMP':
            sector = 'ES_IND'
        elif index == 'TS_DHN_SEASONAL':
            sector = 'ES_DHN'
        elif index == 'LFO_STORAGE':
            sector = 'ES_OIL'
        else:
            sector = index
        if not ds_inputs == None:
            try:
                max_flex_demand = ds_inputs['XVarDemand'][i].loc[ds_inputs['XVarDemand'][i][sector].idxmax(), sector]
            except:
                max_flex_demand = 0
            try:
                max_flex_supply = ds_inputs['XVarSupply'][i].loc[ds_inputs['XVarSupply'][i][sector].idxmax(), sector]
            except:
                max_flex_supply = 0
        boundary_sector_inputs = assign_parameters_by_index(boundary_sector_inputs, sector,
                                                            ['Sector', 'STOCapacity', 'STOSelfDischarge',
                                                             'MaxFlexDemand', 'MaxFlexSupply'],
                                                            [sector, storage_capacity, storage_self_discharge,
                                                             max_flex_demand, max_flex_supply])
    # %% ---------------------------------------------- For non-CHP units ----------------------------------------------
    power_plants = assign_typical_values(power_plants, typical_units, ['CHP', 'P2GS'], 'mean', 1000, 1000)

    # %% ------------------------------------------------ For CHP units ------------------------------------------------
    power_plants = assign_typical_values(power_plants, typical_units,
                                         ['HEAT', 'ELEC', 'STO', 'P2GS', 'P2HT', 'P2GS_STO'], 'mean', 1000, 1000)

    # %% ------------------------------------------------ For P2GS units -----------------------------------------------
    power_plants = assign_typical_values(power_plants, typical_units,
                                         ['HEAT', 'ELEC', 'STO', 'CHP', 'P2HT', 'P2GS_STO'], 'mean', 1000, 1000)

    # %% ------------ Last stuff to do ------------
    # Change the value of the Zone - TO IMPROVE WITH SEVERAL COUNTRIES
    power_plants = assign_parameters(power_plants, assign_zone(zone_name='ES', zone=zone, method='single'), 'Zone')
    power_plants = assign_parameters(power_plants, assign_zone(zone_name=power_plants.index, zone=zone), 'Unit')

    # Sort columns as they should be
    if dispaset_version == '2.5':
        power_plants = pd.DataFrame(power_plants, columns=column_names)
    if dispaset_version == '2.5_BS':
        power_plants = pd.DataFrame(power_plants, columns=column_names_bs)
        column_names_bs_input = ['Sector', 'STOCapacity', 'STOSelfDischarge', 'MaxFlexDemand', 'MaxFlexSupply',
                                 'STOMinSOC']
        boundary_sector_inputs = pd.DataFrame(boundary_sector_inputs, columns=column_names_bs_input)

    # Assign water consumption
    power_plants.loc[:, 'WaterWithdrawal'] = 0
    power_plants.loc[:, 'WaterConsumption'] = 0

    allunits = power_plants
    allunits = allunits[(allunits['PowerCapacity'] * allunits['Nunits'] >= technology_threshold) |
                        (allunits['STOMaxChargingPower'] * allunits['Nunits'] >= technology_threshold)]

    if dispaset_version == '2.5':
        if write_csv:
            write_csv_files(file_name, allunits, 'PowerPlants', index=False, write_csv=True)
        return allunits
    if dispaset_version == '2.5_BS':
        boundary_sector_inputs.reset_index(col_level='Sector', drop=True, inplace=True)
        if write_csv:
            write_csv_files(file_name, allunits, 'PowerPlants', index=False, write_csv=True)
            write_csv_files('BoundarySectorInputs', boundary_sector_inputs, 'BoundarySectorInputs', index=True,
                            write_csv=True)
        return allunits, boundary_sector_inputs
