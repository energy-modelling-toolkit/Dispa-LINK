"""
This script generates the Scaled Inflows time series for Dispa-SET
Input : hinflw_w.dat chidrobo.csv
Output : Database/Scaled_Inflows/'Scaled_Inflows + str(year) + '.csv'

@authors:
                Marco Navia, UMSS
                Isaline Gomand, ULiege            
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven
               
@supervision:
                Sylvain Quoilin, KU Leuven, ULiege

"""
import numpy as np
import pandas as pd
import datetime

InflowsSDDP = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/hinflw_w.dat', header=0, colspecs="infer", engine='python')
InflowsSDDP[['Etapa','Año']] = InflowsSDDP['1/1979'].str.split('/',expand=True)
InflowsSDDP = InflowsSDDP.iloc[:,1:] 
PlantsSDDP = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/chidrobo.csv', header=0)

# Datetime by week
df_week = pd.DataFrame(index=pd.date_range(start='1979-01-01 00:00:00+00:00', end='2021-12-31 23:00:00+00:00', freq='W'), 
                        columns=PlantsSDDP['...Nombre...'])
df_week.loc[pd.Timestamp('2021-12-31 23:00:00+00:00')]=0

# Create inflows dataframe with hourly resolution
for year in range(1979, 2022):
    d = datetime.date(year, 12, 28)
    if d.isocalendar()[1] == 53:
        next_year = year + 1
        new_row = InflowsSDDP.loc[(InflowsSDDP['Año'] == str(next_year)) & (InflowsSDDP['Etapa'] == str(1))].copy()      
        InflowsSDDP = InflowsSDDP.append(new_row)
InflowsSDDP = InflowsSDDP.iloc[:,:-2].sort_index()
InflowsSDDP.columns = InflowsSDDP.columns.astype('int64')
diccionario = dict(zip(PlantsSDDP['.PV.'], PlantsSDDP['...Nombre...']))
InflowsSDDP = InflowsSDDP.rename(columns=diccionario).set_index(df_week.index)     
df = pd.DataFrame(index=pd.date_range(start='1979-01-01 00:00:00+00:00', end='2021-12-31 23:00:00+00:00', freq='H'), 
                        columns=InflowsSDDP.columns) 
df.iloc[[0,-1],:] = InflowsSDDP.iloc[[0,-1],:]
df.loc[InflowsSDDP.index, :] = InflowsSDDP.loc[InflowsSDDP.index, :]
df = df.astype('float64').interpolate()

# Qmax by unit
QMax = pd.DataFrame(PlantsSDDP['.QMax..']).set_index(PlantsSDDP['...Nombre...'])
    
#Aproximation of Outflow and Spillage for units "_LG" "_CA" "_TO"
def get_storage_outputs(InflowsPerSec, dam_name='', STORAGE=0, Qm=0):
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
ANGLG = get_storage_outputs(df, dam_name='ANGLG', STORAGE=PlantsSDDP.at[5, '.VMax..']*10E5, Qm=PlantsSDDP.at[5, '.QMax..'])
df.loc[:,'ANG'] = df[:]['ANG']+ANGLG[:]['OUTFLOW'].values+ANGLG[:]['Spillage'].values
df.loc[:,'CHO'] = df[:]['CHO']+df[:]['ANG'].clip(upper=float(QMax.loc['ANG']))+df[:]['MIG']
df.loc[:,'CRB'] = df[:]['CRB']+df[:]['CHO']+df[:]['CRBLG']+(df[:]['ANG']-df[:]['ANG'].clip(upper=float(QMax.loc['ANG'])))
df.loc[:,'CARABUCO_TO'] = df[:]['CARABUCO_TO']+df[:]['CRB'].clip(upper=float(QMax.loc['CRB']))

CHUCALOMA_TO = get_storage_outputs(df, dam_name='CHUCALOMA_TO', STORAGE=PlantsSDDP.at[36, '.VMax..']*10E5, Qm=PlantsSDDP.at[36, '.QMax..'] )
df.loc[:,'CHACAJAHU_TO'] = df[:]['CHACAJAHU_TO']+CHUCALOMA_TO[:]['OUTFLOW'].values

CALACHAUM_LG = get_storage_outputs(df, dam_name='CALACHAUM_LG', STORAGE=PlantsSDDP.at[34, '.VMax..']*10E5, Qm=PlantsSDDP.at[34, '.QMax..'] )
df.loc[:,'CALACHAKA_TO'] = df[:]['CALACHAKA_TO']+CALACHAUM_LG[:]['OUTFLOW'].values+CALACHAUM_LG[:]['Spillage'].values

CALACHAKA_TO = get_storage_outputs(df, dam_name='CALACHAKA_TO', STORAGE=PlantsSDDP.at[35, '.VMax..']*10E5, Qm=PlantsSDDP.at[35, '.QMax..'])

CARABUCO_TO = get_storage_outputs(df, dam_name='CARABUCO_TO', STORAGE=PlantsSDDP.at[38, '.VMax..']*10E5, Qm=PlantsSDDP.at[38, '.QMax..'])
CHACAJAHU_TO = get_storage_outputs(df, dam_name='CHACAJAHU_TO', STORAGE=PlantsSDDP.at[37, '.VMax..']*10E5, Qm=PlantsSDDP.at[37, '.QMax..'] )
df.loc[:,'UMAPALCA_CA'] = df[:]['UMAPALCA_CA']+CARABUCO_TO[:]['OUTFLOW'].values+CHACAJAHU_TO[:]['OUTFLOW'].values+CALACHAKA_TO[:]['OUTFLOW'].values

UMAPALCA_CA = get_storage_outputs(df, dam_name='UMAPALCA_CA', STORAGE=PlantsSDDP.at[39, '.VMax..']*10E5, Qm=PlantsSDDP.at[39, '.QMax..'] )
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

for year in range(1979, 2022):
    ScaledInflows.loc[str(year)].to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Scaled_Inflows/' + str(year) + '.csv')

# multipliers = dict(zip(PlantsSDDP['...Nombre...'], PlantsSDDP['....Pot']))
# ExpecGen = ((ScaledInflows.resample('Y').sum()).apply(lambda x: x * multipliers[x.name], axis=0))*0.000001
# ExpecGen = ExpecGen.loc[:,(ExpecGen!=0).any(axis=0)]
# ExpecGen.to_csv('../04_DISPASET_DATABASE/Scaled_Inflows/ExpecGen.csv')