# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 20:41:12 2017
 
@author: sylvain
"""
from __future__ import division
import numpy as np
import pandas as pd
import os, sys
import datetime
import itertools
from typing import List, Optional, Union

# %%

entsoe_types = ['Wind Onshore ',
                'Geothermal ',
                'Hydro Water Reservoir ',
                'Hydro Pumped Storage ',
                'Nuclear ',
                'Hydro Run-of-river and poundage ',
                'Solar ',
                'Biomass ',
                'Other renewable ',
                'Fossil Brown coal/Lignite ',
                'Marine ',
                'Fossil Oil ',
                'Fossil Peat ',
                'Wind Offshore ',
                'Waste ',
                'Fossil Hard coal ',
                'Fossil Oil shale ',
                'Fossil Gas ',
                'Fossil Coal-derived gas ',
                'Other ']

# %%

'''
Dictionary with the common variable definitions
to be used in Dispa-SET
'''
commons = {'TimeStep': '1h',
           'Technologies': ['HDAM', 'HROR', 'HPHS', 'PHOT', 'WAVE', 'WHEN', 'WTOF', 'WTON',
                            'COMC', 'GTUR', 'ICEN', 'SCSP', 'STUR',
                            'BATS', 'BEVS', 'CAES', 'P2GS', 'THMS',
                            'ABHP', 'ASHP', 'GETH', 'GSHP', 'HOBO', 'HYHP', 'P2HT', 'REHE', 'SOTH', 'WSHP'],
           'tech_renewables': ['HROR', 'PHOT', 'WAVE', 'WTOF', 'WTON', 'SOTH'],
           'tech_storage': ['HDAM', 'HPHS', 'BATS', 'BEVS', 'CAES', 'THMS', 'P2GS', 'SCSP'],
           'tech_p2ht': ['P2HT', 'ABHP', 'ASHP', 'GSHP', 'HYHP', 'WSHP', 'REHE'],
           'tech_heat': ['GETH', 'HOBO', 'SOTH'],
           'types_CHP': ['extraction', 'back-pressure', 'p2h'],
           'Fuels': ['AIR', 'BIO', 'GAS', 'HRD', 'LIG', 'NUC', 'OIL', 'PEA', 'SUN', 'WAT', 'WIN',
                     'WST', 'OTH', 'GEO', 'HYD', 'WHT'],
           }


# %%
def fix_na(series, fillzeros=True, verbose=True, name='', Nstd=4, outliers=None):
    """
    Function that fills zero and n/a values from a time series by interpolating
    from the same hours in the previous and next days

    :param series:  Pandas Series with proper datetime index
    :param fillzeros:   If true, also interpolates zero values in the time series
    :param verbose:     If true, prints information regarding the number of fixed data points
    :param name:        String with the name of the time series, for the display massage
    :param Nstd:        Number of standard deviations to use as threshold for outlier detection
    :param outliers:    List of lists with the start and stop periods to be discarded

    :returns:   Same series with filled nan values
    """
    longname = name + ' ' + str(series.index.freq)
    # turn all zero values into na:
    if fillzeros:
        series[series == 0] = np.nan
    # check for outliers:
    toohigh = series > series.mean() + Nstd * series.std()
    if np.sum(toohigh) > 0:
        print('Time series "' + longname + '": ' + str(
            np.sum(toohigh)) + ' data points unrealistically high. They will be fixed as well')
        series[toohigh] = np.nan
    # write na in all the locations defined as "outlier"
    if outliers:
        count = 0
        for r in outliers:
            idx = (series.index > pd.to_datetime(r[0])) & (series.index < pd.to_datetime(r[-1]))
            series[idx] = np.nan
            count += np.sum(idx)
        print('Time series "' + longname + '": ' + str(count) + ' data points flagged as outliers and removed')

    # Now fix all nan values: 
    loc = np.where(series.isnull())[0]
    print('Time series "' + longname + '": ' + str(len(loc)) + ' data points to fix')
    for i in loc:
        idx = series.index[i]
        # go see if previous days are defined at the same hour:
        left = np.nan
        idxleft = idx + datetime.timedelta(days=-1)
        while np.isnan(left) and idxleft in series.index:
            if np.isnan(series[idxleft]):
                idxleft = idxleft + datetime.timedelta(days=-1)
            else:
                left = series[idxleft]

        right = np.nan
        idxright = idx + datetime.timedelta(days=1)
        while np.isnan(right) and idxright in series.index:
            if np.isnan(series[idxright]):
                idxright = idxright + datetime.timedelta(days=1)
            else:
                right = series[idxright]

        if (not np.isnan(left)) and (not np.isnan(right)):
            series[idx] = (left + right) / 2
        elif (not np.isnan(left)) and np.isnan(right):
            series[idx] = left
        elif np.isnan(left) and (not np.isnan(right)):
            series[idx] = right
        else:
            print('ERROR : no valid data found to fill the data point ' + str(idx))

    return series


def make_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def invert_dic_df(dic, tablename=''):
    """
    Function that takes as input a dictionary of dataframes, and inverts the key of
    the dictionary with the columns headers of the dataframes

    :param dic: dictionary of dataframes, with the same columns headers and the same index
    :param tablename: string with the name of the table being processed (for the error msg)
    :returns: dictionary of dataframes, with swapped headers
    """
    # keys are defined as the keys of the original dictionary, cols are the columns of the original dataframe
    # items are the keys of the output dictionary, i.e. the columns of the original dataframe    
    dic_out = {}
    # First, check that all indexes have the same length:
    index = dic[list(dic.keys())[0]].index
    for key in dic:
        if len(dic[key].index) != len(index):
            sys.exit('The indexes of the data tables "' + tablename + '" are not equal in all the files')

    # Then put the data in a panda Panel with minor orientation:
    panel = pd.Panel.fromDict(dic, orient='minor')
    # Display a warning if some items are missing in the original data:
    for item in panel.items:
        for key in dic.keys():
            if item not in dic[key].columns:
                print(
                    'The column "' + item + '" is not present in "' + key + '" for the "' + tablename + '" data. Zero will be assumed')
        dic_out[item] = panel[item].fillna(0)
    return dic_out


column_names = ['Unit', 'PowerCapacity', 'Nunits', 'Zone', 'Zone_th', 'Zone_h2', 'Technology', 'Fuel', 'Efficiency',
                'MinUpTime', 'MinDownTime', 'RampUpRate', 'RampDownRate', 'StartUpCost_pu', 'NoLoadCost_pu',
                'RampingCost', 'PartLoadMin', 'MinEfficiency', 'StartUpTime', 'CO2Intensity',
                'CHPType', 'CHPPowerToHeat', 'CHPPowerLossFactor', 'COP', 'Tnominal', 'coef_COP_a', 'coef_COP_b',
                'STOCapacity', 'STOSelfDischarge', 'STOMaxChargingPower', 'STOChargingEfficiency', 'CHPMaxHeat',
                'WaterWithdrawal', 'WaterConsumption']

column_names_bs = ['Unit', 'PowerCapacity', 'Nunits', 'Zone', 'Zone_th', 'Zone_h2', 'Technology', 'Fuel', 'Efficiency',
                   'MinUpTime', 'MinDownTime', 'RampUpRate', 'RampDownRate', 'StartUpCost_pu', 'NoLoadCost_pu',
                   'RampingCost', 'PartLoadMin', 'MinEfficiency', 'StartUpTime', 'CO2Intensity',
                   'CHPType', 'CHPPowerToHeat', 'CHPPowerLossFactor', 'COP', 'Tnominal', 'coef_COP_a', 'coef_COP_b',
                   'STOCapacity', 'STOSelfDischarge', 'STOMaxChargingPower', 'STOChargingEfficiency', 'CHPMaxHeat',
                   'WaterWithdrawal', 'WaterConsumption', 'Sector1', 'EfficiencySector1', 'ChargingEfficiencySector1',
                   'Sector2', 'EfficiencySector2', 'ChargingEfficiencySector2',
                   'Sector3', 'EfficiencySector3', 'ChargingEfficiencySector3']


def check_leap(year):
    """
    Check for leap year
    :param year:    Year to be checked
    :return:        True/False
    """
    if 400 != 0 and (100 == 0 or 4 != 0):
        return False
    else:
        return True


def get_date_range(year):
    """
    Return date range for the analysed year
    :param year:    Year to assign date range
    :return:        Date range
    """
    start = pd.to_datetime('1-1-' + str(year))
    if check_leap(year):
        drange = pd.date_range(start, periods=8784, freq='H')
    else:
        drange = pd.date_range(start, periods=8760, freq='H')
    return drange
