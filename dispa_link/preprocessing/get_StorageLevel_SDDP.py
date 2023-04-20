"""
This script generates the Alert Level time series for Dispa-SET
Input : volale.csv chidrobo.csv
Output : Database/AlertLevel.csv

@authors:
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven

@supervision:
                Sylvain Quoilin, KU Leuven, ULiege

"""
import pandas as pd

df = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/rvolfin.csv', encoding='cp1252', header=3)
df.columns = df.columns.str.replace(' ', '')

#hm3 to fraction
hydro = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/chidrobo.csv', usecols=['...Nombre...','.VMax..'], header=0)
divisors = dict(zip(hydro['...Nombre...'], hydro['.VMax..']))
reserlev = (df.iloc[:,3:].apply(lambda x: x / divisors[x.name], axis=0))

#choosing the last year
reserlev = reserlev.loc[143:194]

#create the dataframe with hourly resolution
reserlev.set_index(pd.date_range(start='2025-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='W'), inplace=True)
reserlevh = pd.DataFrame(index=pd.date_range(start='2025-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H'), 
                        columns=reserlev.columns)
reserlevh.loc[reserlev.index, :] = reserlev.loc[reserlev.index, :]
reserlevh.iloc[[0,-1],:] = reserlev.iloc[[0,0],:]
reserlevh = reserlevh.astype('float64').interpolate()
reserlevh = reserlevh.clip(upper=1)
reserlevh.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/StorageLevel.csv', header=True, index=True)


