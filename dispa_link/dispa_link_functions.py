import logging
import math
import sys
import pandas as pd

from .search import *  # line to import the dictionary
from .constants import *  # line to import the dictionary


typical_mapping = {'Parameters': ['MinUpTime', 'MinDownTime', 'RampUpRate', 'RampDownRate', 'PartLoadMin',
                                  'MinEfficiency', 'StartUpTime', 'StartUpCost_pu', 'NoLoadCost_pu',
                                  'RampingCost', 'CO2Intensity', 'CHPPowerLossFactor']}


def define_units(names):
    """
    Define Units and name them according to source model names (1-1 mapping)
    :param names:   list of unit names
    :return:        power plant database in Dispa-SET readable format
    """
    power_plants = pd.DataFrame(columns=column_names, index=names)
    logging.info('All unit names (' + ' '.join(map(str,names)) + ') assigned to the power plant DataFrame.')
    return power_plants


def assign_parameters(power_plants, values, parameter):
    """
    Populate power plant database with known parameters such as capacity, technology, fuel (1-1 mapping)
    :param power_plants:    power plant database in Dispa-SET readable format
    :param values:          list of parameter values
    :param parameter:       parameter "PowerCapacity, Efficiency etc."
    :return:                power plant database in Dispa-SET readable format
    """
    power_plants[parameter] = values
    logging.info('Mapping of source model ' + parameter + ' to Dispa-SET ' + parameter + ' complete!')
    return power_plants


def assign_parameters_by_index(power_plants, idx, parameters, values):
    """
    Populate power plant database with known parameters by index (one at a time)
    :param power_plants:    power plant database in Dispa-SET readable format
    :param idx:             index of the power plant
    :param parameters:      parameter "PowerCapacity, Efficiency etc."
    :param values:          list of parameter values
    :return:                power plant database in Dispa-SET readable format
    """
    if power_plants.empty:
        power_plants.loc[idx, parameters] = values
    else:
        power_plants.loc[power_plants.index == idx, parameters] = values
    logging.info('Mapping of source model parameters (' + ', '.join(map(str,parameters)) + ') for ' + str(idx) +
                 ' to Dispa-SET readable parameters (' +
                 ', '.join(map(str,parameters)) + ') complete!')
    return power_plants


def assign_gas_units(power_plants, comc=1, gt=1, stur=1, source_name='CCGT', source_fuel='GAS',
                     gt_name='OCGT', comc_name='CCGT', stur_name='STUR'):
    """
    Assign one capacity to multiple technologies, i.e. one gas technology to multiple gas technologies (1-M mapping)
    :param power_plants:    power plant database in Dispa-SET readable format
    :param comc:            share of combined cycle
    :param gt:              share of gas turbines
    :param stur:            share of steam turbines
    :param source_name:     source model technology name
    :param gt_name:         source gas turbine name
    :param comc_name:       source combined cycle name
    :param stur_name:       source steam turbine name
    :return:                power plant database in Dispa-SET readable format
    """
    power_plants.loc[gt_name + '_' + source_fuel, ['PowerCapacity', 'Technology', 'Fuel', 'Sort']] = \
        [power_plants.loc[source_name, 'PowerCapacity'] * gt / (comc + gt + stur), 'GTUR', source_fuel, 'ELEC']
    power_plants.loc[comc_name + '_' + source_fuel, ['PowerCapacity', 'Technology', 'Fuel', 'Sort']] = \
        [power_plants.loc[source_name, 'PowerCapacity'] * comc / (comc + gt + stur), 'COMC', source_fuel, 'ELEC']
    power_plants.loc[stur_name + '_' + source_fuel, ['PowerCapacity', 'Technology', 'Fuel', 'Sort']] = \
        [power_plants.loc[source_name, 'PowerCapacity'] * stur / (comc + gt + stur), 'STUR', source_fuel, 'ELEC']
    power_plants.drop(source_name, inplace=True)
    return power_plants


def assign_typical_values(power_plants, typical_units, exclude=['CHP', 'P2GS'], clustering_type='mean',
                          power_conversion=1000, storage_conversion=1000, dispaset_version='2.5_BS'):
    """
    Function that assigns typical values from the typical units table.
    :param power_plants:        power plant database in Dispa-SET readable format
    :param typical_units:       typical units dataframe
    :param exclude:             list of units to exclude (located in the SORT column)
    :param clustering_type:     type of clustering when more than one unit of same fuel_technology combination present
    :param power_conversion:    multiplier for converting GW to MW ot any other combination
    :param storage_conversion:  multiplier for converting GWh to MWh ot any other combination
    :return:                    filled in power plant database
    """
    index_list = list(power_plants.loc[(~power_plants['Sort'].isin(exclude))].index.values.tolist())
    for index in index_list:
        series = power_plants.loc[index]
        tech = series['Technology']
        fuel = series['Fuel']
        chp_type = series['CHPType']
        #TODO: check if ok
        if 'CHP' in exclude:
            typical_row = typical_units.loc[(typical_units['Technology'] == tech) & (typical_units['Fuel'] == fuel)]
        elif 'CHP' not in exclude:
            typical_row = typical_units.loc[(typical_units['Technology'] == tech) & (typical_units['Fuel'] == fuel) &
                                            (typical_units['CHPType'] == chp_type)]

            if (typical_row.empty) & (chp_type == 'back-pressure'):
                logging.error('There was no correspondence for the COGEN ' + tech + '_' + fuel + '_' + chp_type +
                              ' in the Typical_Units file (' + index + ')')
                logging.info('Try to find information for ' + tech + fuel + ' and CHPType : Extraction')

                chp_type2 = 'Extraction'
                typical_row = typical_units.loc[
                    (typical_units['Technology'] == tech) & (typical_units['Fuel'] == fuel) & (
                            typical_units['CHPType'] == chp_type2)]
                if not (typical_row.empty):
                    logging.info('Data has been found for ' + tech + '_' + fuel +
                                 ' the CHPType Extraction ; will be set as back-pressure for DS model though')
        else:
            logging.error('Something went wrong!')
            sys.exit(1)
        # If there is no correspondence in Typical_row
        if typical_row.empty:
            logging.error('There was no correspondence for the Technology ' + tech + ' and fuel' + fuel +
                          ' in the Typical_Units file' + '(' + index + '). So the Technology ' + tech + ' and fuel ' +
                          fuel + ' will be dropped from dataset')

            #FIXME: IS THIS the best way to handle the lack of presence in Typical_Units ? - TO IMPROVE
            if 'CHP' in exclude:
                power_plants.drop(index, inplace=True)

        # If the unit is present in Typical_Units.csv
        else:
            for carac in typical_mapping['Parameters']:
                # if CO2 is already assigned skipp it, otherwise assign values from typical units
                if carac == 'CO2Intensity':
                    if power_plants.loc[index, 'CO2Intensity'] in [np.nan, np.NAN, 'nan', '']:
                        value = np.array(typical_row[carac].values)
                    else:
                        value = np.array([power_plants.loc[index, 'CO2Intensity']])
                else:
                    value = typical_row[carac].values

                # Adding the needed characteristics of typical units
                # Take into account the cases where the array is of length :
                #    1) nul : no value, the thing is empty
                #    2) 1 : then everything is fine
                #    3) > 1 : then .. What do we do ?
                if len(value) == 0:
                    logging.error('For characteristics ' + carac + ' no correspondence has been found for the '
                                  'Technology ' + tech + ' and Fuel ' + fuel + '(' + index + ')')
                elif len(value) == 1:  # Normal case
                    value = float(value)
                    power_plants.loc[index, carac] = value
                elif len(value) > 1:
                    if clustering_type == 'mean':
                        power_plants.loc[index, carac] = value.mean()
                        logging.warning('For characteristics ' + carac + ' size of value is > 1 for the Technology ' +
                                        tech + ' and Fuel ' + fuel + '. Mean value will be assigned')
                    else:
                        logging.error('Clustering type: ' + clustering_type + ' selected!! ' + clustering_type +
                                      'is not mean or median. Change!')
                        sys.exit(1)

                if 'CHP' not in exclude:
                    # Fine-tuning depending on the carac and different types of TECH
                    if (carac == 'CHPPowerLossFactor') & (chp_type == 'back-pressure'):
                        if value > 0:
                            logging.warning('The CHP back-pressure unit ' + tech + '_' + fuel +
                                            ' has been assigned a non-0 CHPPowerLossFactor. '
                                            'This value has to be forced to 0 to work with DISPA-SET')
                            power_plants.loc[index, carac] = 0
                # END of the carac loop

            # 1) Capacity from source model is in GW/GWh -> set it in MW/MWh
            power_plants.loc[index, 'PowerCapacity'] = float(power_plants.loc[index, 'PowerCapacity']) * power_conversion
            power_plants.loc[index, 'STOCapacity'] = float(power_plants.loc[index, 'STOCapacity']) * storage_conversion

            if ('P2GS' not in exclude) and (dispaset_version == '2.5_BS'):
                power_plants.loc[index, 'STOMaxChargingPower'] = float(power_plants.loc[index, 'STOMaxChargingPower']) \
                                                                 * storage_conversion

            # 2) Divide the capacity in assets into N_Units
            # Take into account the case where PowerCapacity in TypicalUnits is 0 - (e.g for BEVS, P2HT)
            # The solution is to set the PowerCapacity as the one given by source model and set 1 Nunits
            if typical_row['PowerCapacity'].mean() == 0.:
                number_units = 1
                power_plants.loc[index, 'Nunits'] = number_units
                # If the technology is not implemented in source model, PowerCapacity will be 0
            elif (float(typical_row['PowerCapacity'].mean()) != 0) & (float(series['PowerCapacity']) == 0.):
                if 'P2GS' not in exclude:
                    if dispaset_version == '2.5':
                        number_units = 0
                        power_plants.loc[index, 'Nunits'] = number_units
                    elif dispaset_version == '2.5_BS':
                        number_units = 1
                        power_plants.loc[index, 'Nunits'] = number_units
                else:
                    number_units = 0
                    power_plants.loc[index, 'Nunits'] = number_units
            elif (float(typical_row['PowerCapacity'].mean()) != 0) & (float(series['PowerCapacity']) > 0.):
                number_units = math.ceil(float(power_plants.loc[index, 'PowerCapacity']) /
                                         float(typical_row['PowerCapacity'].mean()))
                power_plants.loc[index, 'Nunits'] = math.ceil(number_units)
                power_plants.loc[index, 'PowerCapacity'] = float(power_plants.loc[index, 'PowerCapacity']) / \
                                                           math.ceil(number_units)

            # 3) P2HT Storage Finish the correspondence for Heat Storage - divide it by the number of units to have
            # it equally shared among the cluster of units If there is a Thermal Storage and then a STOCapacity at
            # the index
            if float(power_plants.loc[index, 'STOCapacity']) > 0:
                # Access the row and column of a dataframe : to get to STOCapacity of the checked tech
                if number_units >= 1:
                    power_plants.loc[index, 'STOCapacity'] = float(power_plants.loc[index, 'STOCapacity']) / number_units
                    power_plants.loc[index, 'STOMaxChargingPower'] = float(power_plants.loc[index, 'STOMaxChargingPower']) / \
                                                                     number_units

    return power_plants


def assign_zone(zone_name=None, zone=None, method='standard'):
    """
    Assign zone names for two cases
    :param zone_name:   Name of a unit or zone
    :param zone:        Single or multi cell
    :param method:      'single' for assigning only nodes and 'standard' for assigning names to units or sectors
    :return:
    """
    if method == 'single':
        if zone is None:
            return zone_name
        else:
            return zone
    if method == 'standard':
        if zone is None:
            return 'ES_' + zone_name
        else:
            return zone + '_' + zone_name