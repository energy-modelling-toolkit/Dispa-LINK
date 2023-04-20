"""
This script generates the Outages time series for Dispa-SET
Input : pmtrsebo.csv ctermibo.csv pmhisebo.csv cgndbo.dat
Output : Database/Outages.csv

@author:
                Marco Navia, UMSS  
@contributors:
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven

@supervision:
                Sylvain Quoilin, KU Leuven, ULiege
"""
import pandas as pd

#outages termal units
dft1 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/pmtrsebo.csv', encoding='cp1252')
dft1 = dft1.fillna(0)
dft1.iloc[:,2:] = dft1.iloc[:,2:]/100
dft1.rename(columns={'Año': 'Year', 'Etapas': 'Week'}, inplace=True)

#taking into account week 53 for 2026
dft1 = dft1.append(dft1.iloc[-1:].copy())
dft1.iloc[-1, dft1.columns.get_loc('Week')] = 53

df_tt = pd.DataFrame(pd.date_range(start='2021-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H'))
df_tt.columns = ['Datetime']
df_tt['Week'], df_tt['Year'] = df_tt['Datetime'].dt.week, df_tt['Datetime'].dt.year
 
outagesterm1 = pd.merge( df_tt, dft1,  how="left", on=['Year','Week'])
outagesterm1 = outagesterm1.fillna(0)
outagesterm1.set_index('Datetime', inplace = True)

dft2 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/ctermibo.csv', usecols=['...Nombre...','..Ih...']).T
dft2.columns = dft2.iloc[0]
dft2 = dft2[1:]/100
dft2 = pd.concat([dft2] * 6, ignore_index=True)
dft2['Year'] = range(2021, 2027)

outagesterm2 = pd.merge( df_tt, dft2,  how="left", on=['Year'])
outagesterm2 = outagesterm2.fillna(0)
outagesterm2.set_index('Datetime', inplace = True)

outagesterm = outagesterm1.add(outagesterm2, fill_value=0)
outagesterm = outagesterm.where(outagesterm <= 1, 1) 
outagesterm = outagesterm.drop(['Year','Week'], axis=1)
# outagesterm1 = outagesterm1.drop(['Year','Week'], axis=1)

#outages hydro units
dfh1 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/pmhisebo.csv', encoding='cp1252')
dfh1 = dfh1.fillna(0)
dfh1.iloc[:,2:] = dfh1.iloc[:,2:]/100
dfh1.rename(columns={'Año': 'Year', 'Etapas': 'Week'}, inplace=True)

#taking into account week 53 for 2026
dfh1 = dfh1.append(dfh1.iloc[-1:].copy())
dfh1.iloc[-1, dfh1.columns.get_loc('Week')] = 53
outageshydro = pd.merge( df_tt, dfh1,  how="left", on=['Year','Week'])
outageshydro = outageshydro.fillna(0)
outageshydro.set_index('Datetime', inplace = True)
outageshydro = outageshydro.drop(['Year','Week'], axis=1)

#outages vres units
dfv1 = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/cgndbo.dat', header=1, colspecs="infer", engine='python',usecols=['!Num Name........','ProbFal'])
dfv1[['Num','Name']] = dfv1['!Num Name........'].str.split(' ',expand=True)

# dfv1 = dfv1.fillna(0)
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
Outages = Outages.drop(['ANGLG','CRBLG','TIQLG','SRO02LG','CHJLG','CALACHAUM_LG','CALACHAKA_TO',
                        'CHUCALOMA_TO','CHACAJAHU_TO','CARABUCO_TO','UMAPALCA_CA','PALILLA01_CA',
                        'JALANCHA_TO','CALACHAMI_TO','PALILLA02_CA','CHORO_TO','KEWANI_TO',
                        'JUNTAS_TO','FICTICIA','MOLLE'], axis=1)
Outages = Outages.loc['2025-12-31 23:00:00+00:00':'2026-12-31 23:00:00+00:00']
Outages.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Outages.csv')