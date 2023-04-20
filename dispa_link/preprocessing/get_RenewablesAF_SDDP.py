"""
This script generates the Availability Factor for Renewable Power sources time series for Dispa-SET
Input : blrenw005bo0_w.dat
Output : Database/RenewablesAF

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

vresaf = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/blrenw005bo0_w.dat',header=1,colspecs="infer", engine='python')
vresaf[['Year','Año','Week','Block','QOL','QOL2','ORU','UYU','YUN','WAR1','SJU','EDO','WAR2','VEN','ORU2']] = vresaf.iloc[:,0].str.split(',',expand=True)
vresaf = vresaf.iloc[:,1:]
vresaf = vresaf.astype('float64')

condiciones =[
              (vresaf['Year'] == 1), 
              (vresaf['Year'] == 2), 
              (vresaf['Year'] == 3), 
              (vresaf['Year'] == 4), 
              (vresaf['Year'] == 5) 
              ]

opciones = [2022,
            2023,
            2024,
            2025,
            2026,
            ] 

vresaf['Year'] = np.select(condiciones,opciones)

# Including week 53
mask = (vresaf['Year'] == 2026) & (vresaf['Week'] == 52)
filtered_vresaf = vresaf.loc[mask]
filtered_vresaf['Week'] = filtered_vresaf['Week'].replace(52,53) 
vresaf = vresaf.append(filtered_vresaf)

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
    
RenewablesAF = pd.merge( df_t, vresaf,  how="left", on=['Year','Week', 'Block'])
RenewablesAF.set_index('Datetime',inplace=True, drop=True)
# Select year 2026
RenewablesAF = RenewablesAF.loc['2025-12-31 23:00:00+00:00':'2026-12-31 23:00:00+00:00']
RenewablesAF = RenewablesAF.iloc[:,6:]

RenewablesAF.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/RenewablesAF.csv')