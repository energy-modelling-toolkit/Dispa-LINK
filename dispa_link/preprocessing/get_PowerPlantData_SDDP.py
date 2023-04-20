"""
This script generates the PowerPlant file for Dispa-SET
Input : chidrobo.csv ctermibo.csv cgndbo.dat dbus.csv BusList-ZONES1.csv
Output : Database/PowerPlantData.csv

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

hydro = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/chidrobo.csv', header=0, usecols=['...Nombre...','....Pot','.VMax..','.FPMed.'])
hydro = hydro.rename({'...Nombre...':'Unit','....Pot':'PowerCapacity'}, axis=1)	

thermo = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/ctermibo.csv', header=0, usecols=['...Nombre...','.PotIns','Comb'])
thermo = thermo.rename({'...Nombre...':'Unit','.PotIns':'PowerCapacity','Comb':'Fuel'}, axis=1)	

vres = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/cgndbo.dat', header=1, colspecs="infer", engine='python', usecols=['!Num Name........','.PotIns'])
vres[['Num','Unit']] = vres['!Num Name........'].str.split(' ',expand=True)
vres = vres.rename({'Name':'Unit','.PotIns':'PowerCapacity'}, axis=1)	
vres['Num'] = vres['Num'].astype('float64')

dbus = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/dbus.csv',encoding='cp1252', header=1, usecols= ['Name','Gen. name'])
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
plthydro[['Technology','Fuel','STOCapacity']] = ['HDAM','WAT',(plthydro['.VMax..'] * plthydro['.FPMed.'] * 10000)/36]

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
pltvres = pd.merge(vres, dbus,  how="left", on=['Unit'])
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

opt1 = [1,0.35,0.35,0.31,1,1]
opt2 = [0,0,0,0,0,0]
opt3 = [0,0,0,0,0,0]
opt4 = [0.06666667,0.06666667,0.06666667,0.06666667,0.02,0.02]
opt5 = [0.06666667,0.06666667,0.06666667,0.06666667,0.02,0.02]
opt6 = [0,25,25,25,0,0]
opt7 = [0,0,0,0,0,0]
opt8 = [0,0.8,0.8,0.8,0,0]
opt9 = [0,0.3,0.3,0.3,0,0]
opt10 = [1,0.33,0.33,0.33,1,1]
opt11 = [0,0,0,0,0,0]
opt12 = [0,0.574,0.755,0,0,0]
opt13 = ['','','','','','']
opt14 = ['','','','','','']
opt15 = [0.0000001,'','','','','']
opt16 = [0,'','','','','']
opt17 = [0.8,'','','','','']
opt18 = [1,1,1,1,1,1]

ppd['Efficiency'] = np.select(cond, opt1)
ppd['MinUpTime'] = np.select(cond, opt2)
ppd['MinDownTime'] = np.select(cond, opt3)
ppd['RampUpRate'] = np.select(cond, opt4)
ppd['RampDownRate'] = np.select(cond, opt5)
ppd['StartUpCost'] = np.select(cond, opt6)
ppd['NoLoadCost'] = np.select(cond, opt7)
ppd['RampingCost'] = np.select(cond, opt8)
ppd['PartLoadMin'] = np.select(cond, opt9)
ppd['MinEfficiency'] = np.select(cond, opt10)
ppd['StartUpTime'] = np.select(cond, opt11)
ppd['CO2Intensity'] = np.select(cond, opt12)
ppd['CHPType'] = np.select(cond, opt13)
ppd['CHPPowerToHeat'] = np.select(cond, opt14)
ppd['STOSelfDischarge'] = np.select(cond, opt15)
ppd['STOMaxChargingPower'] = np.select(cond, opt16)
ppd['STOChargingEfficiency'] = np.select(cond, opt17)
ppd['Nunits'] = np.select(cond, opt18)

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
buslist = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/BusList-ZONES1.csv')
zones = dict(zip(buslist['Busname'], buslist['Zones']))
PowerPlantData.insert(3,'Zone',PowerPlantData['Zones'].map(zones))
PowerPlantData = PowerPlantData.drop('Zones',axis=1)
PowerPlantData.set_index('PowerCapacity',inplace=True, drop=True)

PowerPlantData.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/PowerPlantData.csv') 












