"""
This script generates the Demand time series for Dispa-SET
Input : dbf005bo.dat
Output : Database/Demand.csv.csv

@author:
                Marco Navia, UMSS  
@contributors:
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven

@supervision:
                Sylvain Quoilin, KU Leuven, ULiege
                
"""
import numpy as np
import pandas as pd
from functools import reduce

df = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dbf005bo.dat', encoding='cp1252', header=0, colspecs="infer", engine='python')
df['dd/mm/yyyy'] = pd.to_datetime(df['dd/mm/yyyy'], format='%d/%m/%Y')
df1 = df[['..Bus.Name..','Llev','..Load..','dd/mm/yyyy']].rename({'..Bus.Name..':'Busname','Llev':'Block','..Load..':'Load(MW)','dd/mm/yyyy':'Datetime'}, axis=1)
Busname_datalist = df1.Busname.unique()[:, np.newaxis].T

#Buses in different dataframe inside a list
df1 = [df1.loc[df1['Busname'] == busname] for busname in Busname_datalist[0]]
df1 = [df.rename({'Load(MW)': df['Busname'].iat[0]}, axis=1).drop(['Busname'], axis=1) for df in df1]
data_merge = reduce(lambda left, right: pd.merge(left, right, on=('Datetime', 'Block'), how='outer'), df1)
data_merge = data_merge.assign(Weekday=pd.DatetimeIndex(data_merge.Datetime).weekday, Week=pd.DatetimeIndex(data_merge.Datetime).week, Year = pd.DatetimeIndex(data_merge.Datetime).year)

# Including week 53
mask = (data_merge['Year'] == 2026) & (data_merge['Week'] == 52)
filtered_data_merge = data_merge.loc[mask]
filtered_data_merge['Week'] = filtered_data_merge['Week'].replace(52,53) 
data_merge = data_merge.append(filtered_data_merge)
data_merge = data_merge.reset_index(drop=True)

df_t = pd.DataFrame()
df_t['Datetime'] = pd.date_range(start='2021-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H')
df_t = df_t.assign(Weekday=pd.DatetimeIndex(df_t.Datetime).weekday, Hour=pd.DatetimeIndex(df_t.Datetime).hour, Year = pd.DatetimeIndex(df_t.Datetime).year, Week =pd.DatetimeIndex(df_t.Datetime).week)
df_t['Block'] = " "

condiciones =[
    #lunes
              (df_t['Weekday'] == 0)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 0)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 0)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 0)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 0)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 0)&(df_t['Hour'] == 22),
              (df_t['Weekday'] == 0)&(df_t['Hour'] >= 20)&(df_t['Hour'] <= 21),
    #martes
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 1)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 1)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 22),
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 20),
              (df_t['Weekday'] == 1)&(df_t['Hour'] == 21),
    #miercoles                        
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 2)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 2)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 22),
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 20),
              (df_t['Weekday'] == 2)&(df_t['Hour'] == 21),
    #jueves                            
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 3)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 3)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 22),
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 20),
              (df_t['Weekday'] == 3)&(df_t['Hour'] == 21),
    #viernes                            
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 4)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 4)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 22),
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 20),
              (df_t['Weekday'] == 4)&(df_t['Hour'] == 21),
    #sabado              
              (df_t['Weekday'] == 5)&(df_t['Hour'] == 0), 
              (df_t['Weekday'] == 5)&(df_t['Hour'] == 23),
              (df_t['Weekday'] == 5)&(df_t['Hour'] >= 8)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 5)&(df_t['Hour'] >= 1)&(df_t['Hour'] <= 7),
              (df_t['Weekday'] == 5)&(df_t['Hour'] >= 19)&(df_t['Hour'] <= 22),
              
    #domingo             
              (df_t['Weekday'] == 6)&(df_t['Hour'] >= 0)&(df_t['Hour'] <= 18),
              (df_t['Weekday'] == 6)&(df_t['Hour'] == 19), 
              (df_t['Weekday'] == 6)&(df_t['Hour'] >= 20)&(df_t['Hour'] <= 21),
              (df_t['Weekday'] == 6)&(df_t['Hour'] >= 22)&(df_t['Hour'] <= 23)
              ]   

opciones = [4,4,4,5,3,3,2,
            4,4,4,5,3,3,1,2,
            4,4,4,5,3,3,1,2,
            4,4,4,5,3,3,1,2,
            4,4,4,5,3,3,1,2,
            4,4,4,5,3,
            5,4,3,4
            ] 

df_t['Block'] = np.select(condiciones,opciones)
df_t = df_t.drop(['Hour','Weekday'], axis=1)
data_merge = data_merge.drop(['Datetime','Weekday'], axis=1)
demand = pd.merge( df_t, data_merge,  how="left", on=['Year','Week', 'Block'])

# Filtered Demand
demand.set_index('Datetime',inplace=True, drop=True)
filtered_demand = demand.loc['2025-12-31 23:00:00+00:00':'2026-12-31 23:00:00+00:00']
filtered_demand.fillna(0, inplace=True) 

#Including missing buses
df2 = pd.DataFrame(filtered_demand.columns.unique(), columns=['Busname'])

dfc = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dcirc.dat',header=1,colspecs="infer", engine='python', encoding='cp1252')
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

buslist = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/BusList-ZONES1.csv', encoding='cp1252')
zones = dict(zip(buslist['Busname'], buslist['Zones']))
finaldemand = finaldemand.groupby(zones, axis=1).sum()

finaldemand.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Demand.csv')    