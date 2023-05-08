"""
Created on Thu Apr 20 15:51:06 2023

@author: UMSS
"""
import pandas as pd
import numpy as np
from functools import reduce
from mapping_SDDP import *
import datetime

df_t = get_blocks_to_hours()
# start_date, end_date = '2025-12-31 23:00:00+00:00', '2026-12-31 23:00:00+00:00'

def get_alert_level(hydro, SDDP_alert, start_date, end_date):
    """
    Function that returns alert levels considering SDDP simulation for four years and that it starts on April of a year until March of the next year
    :param hydro:       .csv file of hydro power plants data from SDDP
    :param SDDP_alert:  .csv file of weekly alert level data from SDDP for the predicted years
    :param start_date:  the last hour of the year prior to the analyzed year  
    :param end_date:    the last hour of the analized year
    :return:            Alert levels dataframe hourly time-series
    """
    #TODO: Fix all the function descriptions

    #TODO: check if this should be activated by and if statement

    #df_new is used to consider the reservoir initial volume of SDDP as a constraint in the alert level
    df_new = pd.DataFrame(hydro[".VInic."]*hydro[".VMax.."]).T
    df_new.columns = hydro['...Nombre...']
    df_new=df_new.rename({0:156},axis=0)
    SDDP_alert.update(df_new)

    divisors = dict(zip(hydro['...Nombre...'], hydro['.VMax..']))
    alertlev = (SDDP_alert.iloc[:,2:].apply(lambda x: x / divisors[x.name], axis=0))

    #choosing the last year
    alertlev = alertlev.loc[144:195]

    #create the dataframe with hourly resolution
    alertlev.set_index(pd.date_range(start_date, end_date, freq='W'), inplace=True)
    alertlevh = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='H'), columns=alertlev.columns)
    alertlevh.loc[alertlev.index, :] = alertlev.loc[alertlev.index, :]
    alertlevh.iloc[[0,-1],:] = alertlev.iloc[[0,0],:]
    alertlevh = alertlevh.astype('float64').interpolate()
    return alertlevh

def get_demand(SDDP_demand, dfc, buslist, start_date, end_date):
    """
    Function that returns demand
    :param SDDP_demand : .dat file demand by bus, 5 blocks per week
    :param dfc :         .dat file transfer capacity between buses
    :buslist :           where is identified to which zone a bus belongs to
    :return:             demand dataframe hourly time-series
    """
    
    SDDP_demand['dd/mm/yyyy'] = pd.to_datetime(SDDP_demand['dd/mm/yyyy'], format='%d/%m/%Y')
    df1 = SDDP_demand[['..Bus.Name..','Llev','..Load..','dd/mm/yyyy']].rename({'..Bus.Name..':'Busname','Llev':'Block','..Load..':'Load(MW)','dd/mm/yyyy':'Datetime'}, axis=1)
    Busname_datalist = df1.Busname.unique()[:, np.newaxis].T
    
    #Buses in different dataframe inside a list
    df1 = [df1.loc[df1['Busname'] == busname] for busname in Busname_datalist[0]]
    df1 = [SDDP_demand.rename({'Load(MW)': SDDP_demand['Busname'].iat[0]}, axis=1).drop(['Busname'], axis=1) for SDDP_demand in df1]
    data_merge = reduce(lambda left, right: pd.merge(left, right, on=('Datetime', 'Block'), how='outer'), df1)
    data_merge = data_merge.assign(Weekday=data_merge['Datetime'].dt.weekday, Week=data_merge['Datetime'].dt.isocalendar().week, Year=data_merge['Datetime'].dt.isocalendar().year)
    
    # Including week 53
    mask = (data_merge['Year'] == 2026) & (data_merge['Week'] == 52)
    filtered_data_merge = data_merge.loc[mask]
    filtered_data_merge.loc[:, 'Week'] = filtered_data_merge['Week'].replace(52,53) 
    data_merge = pd.concat([data_merge, filtered_data_merge])
    data_merge = data_merge.reset_index(drop=True)
    
    df_t = get_blocks_to_hours(start_date='2021-12-31 23:00:00+00:00', end_date='2026-12-31 23:00:00+00:00')
    # df_t = df_t.drop(['Hour','Weekday'], axis=1)
    #TODO: Please check that blocks are properly mapped
    
    data_merge = data_merge.drop(['Datetime','Weekday'], axis=1)
    demand = pd.merge( df_t, data_merge,  how="left", on=['Year','Week', 'Block'])
    
    # Filtered Demand
    demand.set_index('Datetime',inplace=True, drop=True)
    filtered_demand = demand.loc[start_date:end_date]
    filtered_demand.fillna(0, inplace=True) 
    
    #Including missing buses
    df2 = pd.DataFrame(filtered_demand.columns.unique(), columns=['Busname'])
    dfc.loc[:,'Name']=dfc['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=0,stop=12)
    dfc.loc[:,'MW']=dfc['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=28,stop=36).astype(float)
    dfc=pd.concat([pd.concat([pd.DataFrame(dfc['Name'].str.slice(stop=3) + '-' + dfc['Name'].str.slice(start=3,stop=6))],axis=1),
                    pd.concat([pd.DataFrame(dfc['Name'].str.slice(start=6,stop=9) + '-' + dfc['Name'].str.slice(start=9,stop=12))],axis=1)])
    BusList = dfc['Name'].unique()
    BusList = pd.DataFrame(BusList, columns=['Busname'])
    
    df3 = pd.concat([df2,BusList], ignore_index=True) 
    df3 = df3[~df3.duplicated(keep=False)] 
    
    MissingDemand = df3.T
    MissingDemand.columns = MissingDemand.iloc[0]
    finaldemand = pd.concat([filtered_demand,MissingDemand], axis = 1)
    
    #RENAME BUSBARS THAT HAVE PROBLEMS 
    finaldemand = finaldemand.rename({'CAÑ-069':'CAN-069','MON-115':'MOE-115','THU-069':'TOH-069','THU-230':'TOH-230'}, axis=1)
    finaldemand = finaldemand.drop(finaldemand.index[-1:])
    finaldemand = finaldemand.fillna(0)
    zones = dict(zip(buslist['Busname'], buslist['Zones']))
    finaldemand = finaldemand.groupby(zones, axis=1).sum()
    return finaldemand

def get_NTC(dfc, lines, start_date, end_date):
    """
    Function that returns net transfer capacity
    :param dfc :        .dat file transfer capacity between buses
    :param start_date:  the last hour of the year prior to the analyzed year  
    :param end_date:    the last hour of the analized year
    :return:            Net transfer capacity hourly time-series
    """
    #TODO: check if import can be moved to a different script (SDDP_dispa-mapping)
    # dfc = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dcirc.dat',header=1,colspecs="infer", encoding='cp1252', engine='python')
    dfc.loc[:,'Name']=dfc['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=0,stop=12)
    dfc.loc[:,'MW']=dfc['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=28,stop=36).astype(float)

    dfc=pd.concat([pd.concat([pd.DataFrame(dfc['Name'].str.slice(stop=3) + '-' + dfc['Name'].str.slice(start=3,stop=6)+' -> '
                                          + dfc['Name'].str.slice(start=6,stop=9) + '-' + dfc['Name'].str.slice(start=9,stop=12)),dfc[['MW']]],axis=1),
                    pd.concat([pd.DataFrame(dfc['Name'].str.slice(start=6,stop=9) + '-' + dfc['Name'].str.slice(start=9,stop=12)+' -> '
                                            + dfc['Name'].str.slice(stop=3) + '-' + dfc['Name'].str.slice(start=3,stop=6)),dfc[['MW']]],axis=1)])

    dfc=dfc.set_index('Name').T
    dfc = pd.DataFrame(1,index=pd.date_range(start_date, end_date, freq='H'),columns=dfc.columns)*dfc.loc['MW',:]

    #lines between zones
    #TODO: make as inuts defined by user
    # lines = {'SU -> CE': ['POT-115 -> OCU-115','SUC-230 -> SAN-230','SUC-230 -> MIZ-230'],
    #        'CE -> SU': ['OCU-115 -> POT-115','SAN-230 -> SUC-230','MIZ-230 -> SUC-230'],
    #        'CE -> OR': ['CAR-230 -> YAP-230','CAR-230 -> ARB-230','CAR-500 -> BRE-500'],
    #        'OR -> CE': ['YAP-230 -> CAR-230','ARB-230 -> CAR-230','BRE-500 -> CAR-500'],
    #        'OR -> NO': ['GUA-230 -> PRA-230','GUA-230 -> PRA-(2)'],
    #        'NO -> OR': ['PRA-230 -> GUA-230','PRA-(2) -> GUA-230'],
    #        'CE -> NO': ['SAN-230 -> PCA-230','VIN-230 -> MAZ-230','SAN-230 -> MIG-230'],
    #        'NO -> CE': ['PCA-230 -> SAN-230','MAZ-230 -> VIN-230','MIG-230 -> SAN-230']}

    # NTC file
    ntc = pd.DataFrame()
    for l in lines:
        ntc.loc[:,l]=dfc.loc[:,lines[l]].sum(axis=1)
    ntc.index=pd.date_range(start_date,  end_date, freq='H') 
    return ntc

def get_Outages(dft1,dft2, dfh1,dfv1,start_date, end_date):    
    """
    Function that returns Power Plants' Outages
    : param dft1 :      .csv file of thermal Power Plants' maintenance schedule for five years by week
    : param dft2 :      .csv file of thermal Power Plants' Forced Outage Rate (FOR %)  
    : param dfh1 :      .csv file of Hydro Power Plants' maintenance schedule for five years by week
    : param dfv1 :      .dat file of Renewable Power Plants' failure probability
    : param start_date:  the last hour of the year prior to the analyzed year  
    : param end_date:    the last hour of the analized year
    : return:            Power plants' outages hourly time-series
    """
    
    dft1 = dft1.fillna(0)
    dft1.iloc[:,2:] = dft1.iloc[:,2:]/100
    dft1.rename(columns={'Año': 'Year', 'Etapas': 'Week'}, inplace=True)
    
    #taking into account week 53 for 2026
    dft1 = pd.concat([dft1, dft1.iloc[-1:].copy()])
    dft1.iloc[-1, dft1.columns.get_loc('Week')] = 53
    
    df_tt = pd.DataFrame(pd.date_range(start='2021-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H'))
    df_tt.columns = ['Datetime']
         
    df_tt =df_tt.assign(Week=df_tt['Datetime'].dt.isocalendar().week, Year=df_tt['Datetime'].dt.isocalendar().year)
    
    outagesterm1 = pd.merge( df_tt, dft1,  how="left", on=['Year','Week'])
    outagesterm1 = outagesterm1.fillna(0)
    outagesterm1.set_index('Datetime', inplace = True)
    
    dft3 = dft2[['...Nombre...','..Ih...']].T
    dft3.columns = dft3.iloc[0]
    dft3 = dft3[1:]/100
    dft3 = pd.concat([dft3] * 6, ignore_index=True)
    dft3['Year'] = range(2021, 2027)
    
    outagesterm2 = pd.merge( df_tt, dft3,  how="left", on=['Year'])
    outagesterm2 = outagesterm2.fillna(0)
    outagesterm2.set_index('Datetime', inplace = True)
    
    outagesterm = outagesterm1.add(outagesterm2, fill_value=0)
    outagesterm = outagesterm.where(outagesterm <= 1, 1) 
    outagesterm = outagesterm.drop(['Year','Week'], axis=1)
        
    #outages hydro units
    dfh1 = dfh1.fillna(0)
    dfh1.iloc[:,2:] = dfh1.iloc[:,2:]/100
    dfh1.rename(columns={'Año': 'Year', 'Etapas': 'Week'}, inplace=True)
    
    #taking into account week 53 for 2026
    dfh1 = pd.concat([dfh1, dfh1.iloc[-1:].copy()])
    dfh1.iloc[-1, dfh1.columns.get_loc('Week')] = 53
    outageshydro = pd.merge( df_tt, dfh1,  how="left", on=['Year','Week'])
    outageshydro = outageshydro.fillna(0)
    outageshydro.set_index('Datetime', inplace = True)
    outageshydro = outageshydro.drop(['Year','Week'], axis=1)
    
    #outages vres units
    dfv1[['Num','Name']] = dfv1['!Num Name........'].str.split(' ',expand=True)
    
    dfv1 = dfv1[['Name','ProbFal']].T
    dfv1.columns = dfv1.iloc[0]
    dfv1 = dfv1[1:]/100
    dfv1 = pd.concat([dfv1] * 6, ignore_index=True)
    dfv1['Year'] = range(2021, 2027)
    
    outagesvres = pd.merge( df_tt, dfv1,  how="left", on=['Year'])
    outagesvres.set_index('Datetime', inplace = True)
    outagesvres = outagesvres.drop(['Year','Week'], axis=1)
    
    #merge all the outages
    Outages = pd.merge( outagesterm, outageshydro,  how="left", on=['Datetime']).merge(outagesvres, how="left", on=['Datetime'])
    # Outages = pd.merge( outagesterm1, outageshydro,  how="left", on=['Datetime']).merge(outagesvres, how="left", on=['Datetime'])
    
    #Select year 2026 and delete hydro units that don't generate
    #TODO: maybe drop becase it might not impact Dispa-SET simulation (dispaset doesnt read exces data from csv files)
    # Outages = Outages.drop(['ANGLG','CRBLG','TIQLG','SRO02LG','CHJLG','CALACHAUM_LG','CALACHAKA_TO',
    #                         'CHUCALOMA_TO','CHACAJAHU_TO','CARABUCO_TO','UMAPALCA_CA','PALILLA01_CA',
    #                         'JALANCHA_TO','CALACHAMI_TO','PALILLA02_CA','CHORO_TO','KEWANI_TO',
    #                         'JUNTAS_TO','FICTICIA','MOLLE'], axis=1)
    Outages = Outages.loc[start_date:end_date]
    return Outages

def get_Power_PlantData(hydro,dft2,dfv1,dbus,buslist):
    """
    Function that returns Power Plants' Database
    : param  hydro:      .csv file of hydro power plants data from SDDP
    : param dft2:        .csv file of thermal Power Plants 
    : dfv1:              .dat file of Renewable Power Plants
    : dbus:              .csv file generator name and bus
    : buslist:           where is identified to which zone a bus belongs to
    : return:            .csv file Power Plant' database
    """
    
    hydro = hydro.rename({'...Nombre...':'Unit','....Pot':'PowerCapacity'}, axis=1)	
    thermo = dft2[['...Nombre...','..Ih...','.PotIns','Comb']]
    thermo = thermo.rename({'...Nombre...':'Unit','.PotIns':'PowerCapacity','Comb':'Fuel'}, axis=1)	

    dfv1[['Num','Unit']] = dfv1['!Num Name........'].str.split(' ',expand=True)
    dfv1 = dfv1.rename({'.PotIns':'PowerCapacity'}, axis=1)	
    dfv1['Num'] = dfv1['Num'].astype('float64')   
    dbus = dbus.rename({'Gen. name':'Unit','Name':'Zones'}, axis=1)

    #HIDRO
    plthydro = pd.merge(hydro, dbus,  how="left", on=['Unit'])

    # Removing the units that don´t have generation and conversion factor
    mask = (plthydro['PowerCapacity'] == 0) & (plthydro['.FPMed.'] == 0) & (plthydro['.VMax..'] < 0.3)
    plthydro = plthydro[~mask]
    plthydro.reset_index(inplace = True)
    # Summing storage capacity of lagoons to power plants
    for i, row in plthydro.iterrows():
        if row['.VMax..'] != 0 and row['PowerCapacity'] == 0:
            plthydro.loc[i+1, '.VMax..'] += row['.VMax..']
    mask = (plthydro['PowerCapacity'] == 0) & (plthydro['.FPMed.'] == 0)
    plthydro = plthydro[~mask]

    plthydro[['Technology','Fuel']] = 'HDAM','WAT'
    plthydro['STOCapacity'] = (plthydro['.VMax..'] * plthydro['.FPMed.'] * 10000)/36

    # Removing the units that don´t have generation and conversion factor
    mask = (plthydro['PowerCapacity'] == 0) & (plthydro['.FPMed.'] == 0)
    plthydro = plthydro[~mask]

    # TERMO
    pltthermo = pd.merge(thermo, dbus,  how="left", on=['Unit'])
    pltthermo['Technology'] = 'GTUR'
    condiciones =[
                  (pltthermo['Fuel'] >= 1)&(pltthermo['Fuel'] <= 10), 
                  (pltthermo['Fuel'] >= 12)&(pltthermo['Fuel'] <= 14),
                  (pltthermo['Fuel'] == 11), 
                  (pltthermo['Fuel'] >= 17)&(pltthermo['Fuel'] <= 21),
                  (pltthermo['Fuel'] >= 15)&(pltthermo['Fuel'] <= 16), 
                  (pltthermo['Fuel'] >= 22)&(pltthermo['Fuel'] <= 24),
                  ]
    opciones = ['GAS',
                'GAS',
                'OIL',
                'OIL',
                'BIO',
                'BIO'
                ] 
    pltthermo['Fuel'] = np.select(condiciones,opciones)
    pltthermo['STOCapacity'] = ''

    ##VRES
    pltvres = pd.merge(dfv1, dbus,  how="left", on=['Unit'])
    condiciones1 =[
                  (pltvres['Num'] >= 1)&(pltvres['Num'] <= 2), 
                  (pltvres['Num'] >= 10)&(pltvres['Num'] <= 18),
                  (pltvres['Num'] >= 5)&(pltvres['Num'] <= 9),
                  ]
    opciones1 = ['WTON',
                'WTON',
                'PHOT',
                ] 
    opciones2 = ['WIN',
                'WIN',
                'SUN',
                ] 
    pltvres['Technology'] = np.select(condiciones1,opciones1)
    pltvres['Fuel'] = np.select(condiciones1,opciones2)
    pltvres['STOCapacity'] = ''

    frames = [plthydro, pltthermo, pltvres]
      
    PowerPlantData = pd.concat(frames)

    #PARA QUE ENDE PONGA VALORES DE SUS UNIDADES GENERADORAS
    # PowerPlantData['Nunits'] = 1
    # PowerPlantData[['Efficiency','MinUpTime','MinDownTime','RampUpRate',
    #                'RampDownRate','StartUpCost','NoLoadCost','RampingCost',
    #                'PartLoadMin','MinEfficiency','StartUpTime','CO2Intensity',
    #                'STOSelfDischarge','STOMaxChargingPower',
    #                'STOChargingEfficiency']] = 'ENDE'

    # PowerPlantData[['CHPType','CHPPowerToHeat']] = 0

    #Assign typical values
    ppd = PowerPlantData

    cond = [
            ppd['Fuel']=='WAT',
            ppd['Fuel']=='GAS',
            ppd['Fuel']=='OIL',
            ppd['Fuel']=='BIO',
            ppd['Fuel']=='WIN',
            ppd['Fuel']=='SUN']

    #TODO: improve it so that its part of the ppd dataframe

    ppd['Efficiency'] = np.select(cond, [1,0.35,0.35,0.31,1,1])
    ppd['MinUpTime'] = np.select(cond, [0,0,0,0,0,0])
    ppd['MinDownTime'] = np.select(cond, [0,0,0,0,0,0])
    ppd['RampUpRate'] = np.select(cond, [0.06666667,0.06666667,0.06666667,0.06666667,0.02,0.02])
    ppd['RampDownRate'] = np.select(cond, [0.06666667,0.06666667,0.06666667,0.06666667,0.02,0.02])
    ppd['StartUpCost'] = np.select(cond, [0,25,25,25,0,0])
    ppd['NoLoadCost'] = np.select(cond, [0,0,0,0,0,0])
    ppd['RampingCost'] = np.select(cond, [0,0.8,0.8,0.8,0,0])
    ppd['PartLoadMin'] = np.select(cond, [0,0.3,0.3,0.3,0,0])
    ppd['MinEfficiency'] = np.select(cond, [1,0.33,0.33,0.33,1,1])
    ppd['StartUpTime'] = np.select(cond, [0,0,0,0,0,0])
    ppd['CO2Intensity'] = np.select(cond, [0,0.574,0.755,0,0,0])
    ppd['CHPType'] = np.select(cond, ['','','','','',''])
    ppd['CHPPowerToHeat'] = np.select(cond, ['','','','','',''])
    ppd['STOSelfDischarge'] = np.select(cond, [0.0000001,'','','','',''])
    ppd['STOMaxChargingPower'] = np.select(cond, [0,'','','','',''])
    ppd['STOChargingEfficiency'] = np.select(cond, [0.8,'','','','',''])
    ppd['Nunits'] = np.select(cond, [1,1,1,1,1,1])

    #order dataframe
    PowerPlantData = ppd
    PowerPlantData = PowerPlantData[['PowerCapacity','Unit','Zones','Technology','Fuel',
                                     'Efficiency','MinUpTime','MinDownTime','RampUpRate',
                                     'RampDownRate','StartUpCost','NoLoadCost','RampingCost',
                                     'PartLoadMin','MinEfficiency','StartUpTime','CO2Intensity',
                                     'CHPType','CHPPowerToHeat','STOCapacity','STOSelfDischarge',
                                     'STOMaxChargingPower','STOChargingEfficiency','Nunits']] 

    #Assign specific STOSelfDischarge values for some hydro power plants
    condition = (PowerPlantData['Unit'] == 'COR') | (PowerPlantData['Unit'] == 'MIG') | (PowerPlantData['Unit'] == 'ANG') | (PowerPlantData['Unit'] == 'ZON') | (PowerPlantData['Unit'] == 'MIS')
    PowerPlantData.loc[condition, 'STOSelfDischarge'] = [0.0000005, 0.00000007, 0.00000008, 0.00000006, 0.00000005]
    # Assining zones
    zones = dict(zip(buslist['Busname'], buslist['Zones']))
    PowerPlantData.insert(3,'Zone',PowerPlantData['Zones'].map(zones))
    PowerPlantData = PowerPlantData.drop('Zones',axis=1)
    PowerPlantData.set_index('PowerCapacity',inplace=True, drop=True)
    return PowerPlantData

def get_renewables_AF(vresaf,start_date, end_date):
    """
    Function that returns Power Plants' Database
    : param  vresaf:      .dat renewables availability factor from SDDP for 5 years
    : param start_date:  the last hour of the year prior to the analyzed year  
    : param end_date:    the last hour of the analized year
    : return:            .csv file renweables Availability Factor hourly time-series
    """
    vresaf[['Year','Año','Week','Block','QOL','QOL2','ORU','UYU','YUN','WAR1','SJU','EDO','WAR2','VEN','ORU2']] = vresaf.iloc[:,0].str.split(',',expand=True)
    vresaf = vresaf.iloc[:,1:]
    vresaf = vresaf.astype('float64')

    options_dict = {1: 2022, 2: 2023, 3: 2024, 4: 2025, 5: 2026}
    vresaf['Year'] = vresaf['Year'].map(options_dict)
       
    # Including week 53
    mask = (vresaf['Year'] == 2026) & (vresaf['Week'] == 52)
    filtered_vresaf = vresaf.loc[mask]
    filtered_vresaf['Week'] = filtered_vresaf['Week'].replace(52,53) 
    vresaf = pd.concat([vresaf, filtered_vresaf])

    # TODO: Please check that blocks are properly mapped     
    df_t = get_blocks_to_hours(start_date='2021-12-31 23:00:00+00:00', end_date='2026-12-31 23:00:00+00:00')
    RenewablesAF = pd.merge( df_t, vresaf,  how="left", on=['Year','Week', 'Block'])
    RenewablesAF.set_index('Datetime',inplace=True, drop=True)
    # Select year 2026
    RenewablesAF = RenewablesAF.loc[start_date:end_date]
    RenewablesAF = RenewablesAF.iloc[:,6:]
    return RenewablesAF

def get_Spillage_Cost(hydro,start_date, end_date):
    """
    Function that returns Spillage cost
    : param  hydro:      .csv file of hydro power plants data from SDDP
    : param start_date:  the last hour of the year prior to the analyzed year  
    : param end_date:    the last hour of the analized year
    : return:            .csv file Spillage cost hourly time-series
    """
    hydro.set_index("...Nombre...",drop=True,inplace=True)
    
    # Units conversion to dollars/MWh 
    hydro= pd.DataFrame(hydro["C.Vert."]/hydro['.FPMed.']*3.6).T
    
    Spilcost = pd.DataFrame(1,index=pd.date_range(start_date, end_date, freq='H'),columns=hydro.columns)*hydro.loc[0,:]
    Spilcost.replace([np.inf, -np.inf], 0, inplace=True) 
    return Spilcost

def get_Storage_lev(SDDP_lev,hydro,start_date, end_date):
    """
    This function returns storage levels for hydro dams
    :param SDDP_lev:    .csv SDDP weekly reservoir level for the simulated years
    :param hydro:       .csv file of hydro power plants data from SDDP
    :return:            Reservoir level df hourly times-series
    """
    hydro = hydro.reset_index()
    SDDP_lev.columns = SDDP_lev.columns.str.replace(' ', '')
    divisors = dict(zip(hydro['...Nombre...'], hydro['.VMax..']))
    reserlev = (SDDP_lev.iloc[:,3:].apply(lambda x: x / divisors[x.name], axis=0))

    #choosing the last year
    reserlev = reserlev.loc[143:194]

    #create the dataframe with hourly resolution
    reserlev.set_index(pd.date_range(start_date, end_date, freq='W'), inplace=True)
    reserlevh = pd.DataFrame(index=pd.date_range(start_date, end_date, freq='H'), columns=reserlev.columns)
    reserlevh.loc[reserlev.index, :] = reserlev.loc[reserlev.index, :]
    reserlevh.iloc[[0,-1],:] = reserlev.iloc[[0,0],:]
    reserlevh = reserlevh.astype('float64').interpolate()
    reserlevh = reserlevh.clip(upper=1)
    return reserlevh

def get_Scaled_inflows(InflowsSDDP,hydro):
    """
    This function returns the scaled inflows of hydro power plants
    :param InflowsSDDP:    .dat file SDDP weekly inflows from 1979 to 2021
    :param hydro:          .csv file of hydro power plants data from SDDP
    :return:               Scaled inflows hourly times-series for 43 years 
    """
    hydro = hydro.reset_index()
    InflowsSDDP[['Etapa','Año']] = InflowsSDDP['1/1979'].str.split('/',expand=True)
    InflowsSDDP = InflowsSDDP.iloc[:,1:] 
    # Datetime by week
    df_week = pd.DataFrame(index=pd.date_range(start='1979-01-01 00:00:00+00:00', end='2021-12-31 23:00:00+00:00', freq='W'), 
                            columns=hydro['...Nombre...'])
    df_week.loc[pd.Timestamp('2021-12-31 23:00:00+00:00')]=0

    # Create inflows dataframe with hourly resolution
    for year in range(1979, 2022):
        d = datetime.date(year, 12, 28)
        if d.isocalendar()[1] == 53:
            next_year = year + 1
            new_row = InflowsSDDP.loc[(InflowsSDDP['Año'] == str(next_year)) & (InflowsSDDP['Etapa'] == str(1))].copy()      
            # InflowsSDDP = InflowsSDDP.append(new_row)
            InflowsSDDP = pd.concat([InflowsSDDP,new_row],ignore_index=True)
    InflowsSDDP = InflowsSDDP.iloc[:,:-2].sort_index()
    InflowsSDDP.columns = InflowsSDDP.columns.astype('int64')
    diccionario = dict(zip(hydro['.PV.'], hydro['...Nombre...']))
    InflowsSDDP = InflowsSDDP.rename(columns=diccionario).set_index(df_week.index)     
    df = pd.DataFrame(index=pd.date_range(start='1979-01-01 00:00:00+00:00', end='2021-12-31 23:00:00+00:00', freq='H'), 
                            columns=InflowsSDDP.columns) 
    df.iloc[[0,-1],:] = InflowsSDDP.iloc[[0,-1],:]
    df.loc[InflowsSDDP.index, :] = InflowsSDDP.loc[InflowsSDDP.index, :]
    df = df.astype('float64').interpolate()

    # Qmax by unit
    QMax = pd.DataFrame(hydro['.QMax..']).set_index(hydro['...Nombre...'])
        
    #Aproximation of Outflow and Spillage for units "_LG" "_CA" "_TO"
    def get_storage_outputs(InflowsPerSec, dam_name='', STORAGE=0, Qm=0):
        """
        Parameters
        ----------
        InflowsPerSec : TYPE
            DESCRIPTION.
        dam_name : TYPE, optional
            DESCRIPTION. The default is ''.
        STORAGE : TYPE, optional
            DESCRIPTION. The default is 0.
        Qm : TYPE, optional
            DESCRIPTION. The default is 0.

        Returns
        -------
        None.

        """
        
        df=InflowsPerSec[dam_name]
        df=pd.DataFrame(df, columns=[dam_name])    
        df = df.assign(**{'OUTFLOW': [None] * len(df), 'StoreLev': [None] * len(df), 'Spillage': [None] * len(df)})
        new_row = pd.Series([0,Qm,STORAGE, 0], index=[dam_name,'OUTFLOW', 'StoreLev','Spillage'])
        new_row =pd.DataFrame([new_row])
        df = pd.concat([new_row,df],ignore_index=True)
        for i in range(len(df)):
            if i > 0:
                if df.loc[i-1,'StoreLev']+ df.loc[i,dam_name]*3600>= Qm*3600:
                    df.loc[i,'OUTFLOW']=Qm
                else:
                    df.loc[i,'OUTFLOW']=df.loc[i,dam_name]
                df.loc[i,'StoreLev']=min(df.loc[i,dam_name]*3600-df.loc[i,'OUTFLOW']*3600+df.loc[i-1,'StoreLev'],STORAGE)
                if STORAGE< df.loc[i,dam_name]*3600-df.loc[i,'OUTFLOW']*3600+df.loc[i-1,'StoreLev']:
                    df.loc[i,'Spillage']=(df.loc[i,dam_name]*3600-df.loc[i,'OUTFLOW']*3600+df.loc[i-1,'StoreLev']-STORAGE)/3600
                else:
                    df.loc[i,'Spillage']=0    
        df = df.tail(-1)
        df.set_index(InflowsPerSec.index, inplace=True)
        return df

    #SISTEMA CORANI
    CORANI=pd.DataFrame(df[:]['COR'].resample('Y').sum())
    CORANI.loc[:,"leap"]=np.where(CORANI.index.is_leap_year.astype(int),8784,8760)
    CORANI.loc[:,"AVGINF"]=CORANI.loc[:,'COR']/CORANI.loc[:,"leap"]
    CORANI = pd.DataFrame(CORANI, index=df.index).bfill(axis="rows").ffill(axis="rows")

    df.loc[:,'SIS'] = df[:]['SIS']+CORANI.loc[:,"AVGINF"]
    df.loc[:,'SJS'] = df[:]['SJS']+df[:]['SIS']+df[:]['FICTICIA']
    df.loc[:,'SJE'] = df[:]['SJE']+df[:]['SJS']
    #SISTEMA YURA
    df.loc[:,'KIL'] = df[:]['KIL']+df[:]['CON']
    df.loc[:,'LAN'] = df[:]['LAN']+df[:]['KIL'].clip(upper=float(QMax.loc['KIL']))
    df.loc[:,'PUH'] = df[:]['PUH']+df[:]['LAN']
    #SISTEMA MISICUNI
    df.loc[:,'MOLLE'] = df[:]['MOLLE']+df[:]['MIS']
    #SISTEMA TAQUESI
    df.loc[:,'CHJ'] = df[:]['CHJ']+df[:]['CHJLG'].clip(upper=float(QMax.loc['KIL']))
    df.loc[:,'YAN'] = df[:]['YAN']+df[:]['CHJ']
    #SISTEMA ZONGO
    df.loc[:,'TIQ'] = df[:]['TIQ']+df[:]['TIQLG'].clip(upper=float(QMax.loc['TIQLG']))
    df.loc[:,'BOT'] = df[:]['BOT']+df[:]['TIQ'].clip(upper=float(QMax.loc['TIQ']))+df[:]['ZON']
    df.loc[:,'CUT'] = df[:]['CUT']+df[:]['BOT']+(df[:]['TIQ']-df[:]['TIQ'].clip(upper=float(QMax.loc['TIQ'])))
    df.loc[:,'SRO01'] = df[:]['SRO01']+df[:]['CUT']
    df.loc[:,'SRO02'] = df[:]['SRO02']+df[:]['SRO02LG']
    df.loc[:,'SAI'] = df[:]['SAI']+df[:]['SRO01']+df[:]['SRO02'].clip(upper=float(QMax.loc['SRO02']))
    df.loc[:,'CHU'] = df[:]['CHU']+df[:]['SAI']+(df[:]['SRO02']-df[:]['SRO02'].clip(upper=float(QMax.loc['SRO02'])))
    df.loc[:,'HAR'] = df[:]['HAR']+df[:]['CHU']
    df.loc[:,'CAH'] = df[:]['CAH']+df[:]['HAR']
    df.loc[:,'HUA'] = df[:]['HUA']+df[:]['CAH']
    #SISTEMA JUNTAS
    df.loc[:,'JUNTAS_TO'] = df[:]['JUNTAS_TO']+(df[:]['SEH']-df[:]['SEH'].clip(upper=float(QMax.loc['SEH'])))
    df.loc[:,'JUN'] = df[:]['JUN']+df[:]['SEH'].clip(upper=float(QMax.loc['SEH']))+df[:]['JUNTAS_TO'].clip(upper=float(QMax.loc['JUNTAS_TO']))
    #SISTEMA MIGUILLAS
    ANGLG = get_storage_outputs(df, dam_name='ANGLG', STORAGE=hydro.at[5, '.VMax..']*10E5, Qm=hydro.at[5, '.QMax..'])
    df.loc[:,'ANG'] = df[:]['ANG']+ANGLG[:]['OUTFLOW'].values+ANGLG[:]['Spillage'].values
    df.loc[:,'CHO'] = df[:]['CHO']+df[:]['ANG'].clip(upper=float(QMax.loc['ANG']))+df[:]['MIG']
    df.loc[:,'CRB'] = df[:]['CRB']+df[:]['CHO']+df[:]['CRBLG']+(df[:]['ANG']-df[:]['ANG'].clip(upper=float(QMax.loc['ANG'])))
    df.loc[:,'CARABUCO_TO'] = df[:]['CARABUCO_TO']+df[:]['CRB'].clip(upper=float(QMax.loc['CRB']))

    CHUCALOMA_TO = get_storage_outputs(df, dam_name='CHUCALOMA_TO', STORAGE=hydro.at[36, '.VMax..']*10E5, Qm=hydro.at[36, '.QMax..'] )
    df.loc[:,'CHACAJAHU_TO'] = df[:]['CHACAJAHU_TO']+CHUCALOMA_TO[:]['OUTFLOW'].values

    CALACHAUM_LG = get_storage_outputs(df, dam_name='CALACHAUM_LG', STORAGE=hydro.at[34, '.VMax..']*10E5, Qm=hydro.at[34, '.QMax..'] )
    df.loc[:,'CALACHAKA_TO'] = df[:]['CALACHAKA_TO']+CALACHAUM_LG[:]['OUTFLOW'].values+CALACHAUM_LG[:]['Spillage'].values

    CALACHAKA_TO = get_storage_outputs(df, dam_name='CALACHAKA_TO', STORAGE=hydro.at[35, '.VMax..']*10E5, Qm=hydro.at[35, '.QMax..'])

    CARABUCO_TO = get_storage_outputs(df, dam_name='CARABUCO_TO', STORAGE=hydro.at[38, '.VMax..']*10E5, Qm=hydro.at[38, '.QMax..'])
    CHACAJAHU_TO = get_storage_outputs(df, dam_name='CHACAJAHU_TO', STORAGE=hydro.at[37, '.VMax..']*10E5, Qm=hydro.at[37, '.QMax..'] )
    df.loc[:,'UMAPALCA_CA'] = df[:]['UMAPALCA_CA']+CARABUCO_TO[:]['OUTFLOW'].values+CHACAJAHU_TO[:]['OUTFLOW'].values+CALACHAKA_TO[:]['OUTFLOW'].values

    UMAPALCA_CA = get_storage_outputs(df, dam_name='UMAPALCA_CA', STORAGE=hydro.at[39, '.VMax..']*10E5, Qm=hydro.at[39, '.QMax..'] )
    df.loc[:,'UMA'] = df[:]['UMA']+UMAPALCA_CA[:]['OUTFLOW'].values
    df.loc[:,'JALANCHA_TO'] = df[:]['JALANCHA_TO']+(df[:]['UMA']-df[:]['UMA'].clip(upper=float(QMax.loc['UMA'])))+CHUCALOMA_TO[:]['Spillage'].values+CHACAJAHU_TO[:]['Spillage'].values

    df.loc[:,'CALACHAMI_TO'] = df[:]['CALACHAMI_TO']+CARABUCO_TO[:]['Spillage'].values+CALACHAKA_TO[:]['Spillage'].values

    df.loc[:,'PALILLA01_CA'] = df[:]['PALILLA01_CA']+df[:]['UMA'].clip(upper=float(QMax.loc['UMA']))+df[:]['CALACHAMI_TO'].clip(upper=float(QMax.loc['CALACHAMI_TO']))+df[:]['JALANCHA_TO'].clip(upper=float(QMax.loc['JALANCHA_TO']))
    df.loc[:,'PALILLA02_CA'] = df[:]['PALILLA02_CA']+df[:]['CHORO_TO'].clip(upper=float(QMax.loc['CHORO_TO']))+df[:]['PALILLA01_CA'].clip(upper=float(QMax.loc['PALILLA01_CA']))
    df.loc[:,'PLD'] = df[:]['PLD']+df[:]['PALILLA02_CA'].clip(upper=float(QMax.loc['PALILLA02_CA']))+df[:]['KEWANI_TO'].clip(upper=float(QMax.loc['KEWANI_TO']))

    # df.to_csv('../04_DISPASET_DATABASE/Scaled_Inflows/Inflows.csv')

    # Scaled inflows
    ScaledInflows = pd.DataFrame(index=df.index, columns=df.columns)
    for unit in df.columns:
        ScaledInflows.loc[:,unit] = df.loc[:,unit]/float(QMax.loc[unit])
    return ScaledInflows
    