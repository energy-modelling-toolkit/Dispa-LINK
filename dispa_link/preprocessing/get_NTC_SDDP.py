"""
This script generates the Net Transfer Capacity time series for Dispa-SET
Input : dcirc.dat
Output : Database/NTC.csv

@authors:
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven

@supervision:
                Sylvain Quoilin, KU Leuven, ULiege
"""
import pandas as pd

# database import
df = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dcirc.dat',header=1,colspecs="infer", encoding='cp1252', engine='python')
df.loc[:,'Name']=df['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=0,stop=12)
df.loc[:,'MW']=df['Nome........(MVAR)(Tmn)(Tmx)(  MW)(MW)'].str.slice(start=28,stop=36).astype(float)

df=pd.concat([pd.concat([pd.DataFrame(df['Name'].str.slice(stop=3) + '-' + df['Name'].str.slice(start=3,stop=6)+' -> '
                                      + df['Name'].str.slice(start=6,stop=9) + '-' + df['Name'].str.slice(start=9,stop=12)),df[['MW']]],axis=1),
                pd.concat([pd.DataFrame(df['Name'].str.slice(start=6,stop=9) + '-' + df['Name'].str.slice(start=9,stop=12)+' -> '
                                        + df['Name'].str.slice(stop=3) + '-' + df['Name'].str.slice(start=3,stop=6)),df[['MW']]],axis=1)])

df=df.set_index('Name').T
df = pd.DataFrame(1,index=pd.date_range(start='2025-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H'),columns=df.columns)*df.loc['MW',:]

#lines between zones
lines = {'SU -> CE': ['POT-115 -> OCU-115','SUC-230 -> SAN-230','SUC-230 -> MIZ-230'],
       'CE -> SU': ['OCU-115 -> POT-115','SAN-230 -> SUC-230','MIZ-230 -> SUC-230'],
       'CE -> OR': ['CAR-230 -> YAP-230','CAR-230 -> ARB-230','CAR-500 -> BRE-500'],
       'OR -> CE': ['YAP-230 -> CAR-230','ARB-230 -> CAR-230','BRE-500 -> CAR-500'],
       'OR -> NO': ['GUA-230 -> PRA-230','GUA-230 -> PRA-(2)'],
       'NO -> OR': ['PRA-230 -> GUA-230','PRA-(2) -> GUA-230'],
       'CE -> NO': ['SAN-230 -> PCA-230','VIN-230 -> MAZ-230','SAN-230 -> MIG-230'],
       'NO -> CE': ['PCA-230 -> SAN-230','MAZ-230 -> VIN-230','MIG-230 -> SAN-230']}

# NTC file
ntc = pd.DataFrame()
for l in lines:
    ntc.loc[:,l]=df.loc[:,lines[l]].sum(axis=1)
ntc.index=pd.date_range(start='2025-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H') 
ntc.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/NTC.csv') 
