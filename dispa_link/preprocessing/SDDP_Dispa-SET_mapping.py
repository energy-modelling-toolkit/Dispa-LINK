# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 16:02:04 2023

@author: UMSS
"""
import get_database_SDDP as sd
import pandas as pd
import os


#Inputs for alert level
SDDP_alert = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/volale.csv', index_col=0, header=3)
SDDP_alert.columns = SDDP_alert.columns.str.replace(' ', '')
hydro = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/chidrobo.csv', usecols=['...Nombre...','.VMax..','.VInic.','....Pot','.FPMed.','C.Vert.','.PV.','.QMax..'], header=0)

#Inputs demand
SDDP_demand = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dbf005bo.dat', encoding='cp1252', header=0, colspecs="infer", engine='python')
dfc = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/dcirc.dat',header=1,colspecs="infer", engine='python', encoding='cp1252')
buslist = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/BusList-ZONES1.csv', encoding='cp1252')
#Inputs outages
#thermal
dft1 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/pmtrsebo.csv', encoding='cp1252')
dft2 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/ctermibo.csv', usecols=['...Nombre...','..Ih...','.PotIns','Comb'])

#hydro
dfh1 = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/pmhisebo.csv', encoding='cp1252')
#vres
dfv1 = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/cgndbo.dat', header=1, colspecs="infer", engine='python',usecols=['!Num Name........','ProbFal','.PotIns'])

dbus = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/dbus.csv',encoding='cp1252', header=1, usecols= ['Name','Gen. name'])

#Renewables availability factor
vresaf = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/blrenw005bo0_w.dat',header=1,colspecs="infer", engine='python')

#reservoirlevel
SDDP_lev = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/rvolfin.csv', encoding='cp1252', header=3)

#ScaledInflows
InflowsSDDP = pd.read_fwf('../../../Dispa-LINK/Inputs/SDDP/hinflw_w.dat', header=0, colspecs="infer", engine='python')

#Results
alertlev = sd.get_alert_level(hydro,SDDP_alert)
finaldemand = sd.get_demand(SDDP_demand, dfc, buslist)
ntc = sd.get_NTC(dfc)
Outages = sd.get_Outages(dft1,dft2, dfh1,dfv1)
PowerPlantData = sd.get_Power_PlantData(hydro,dft2,dfv1,dbus,buslist)
RenewablesAF = sd.get_renewables_AF(vresaf)
Spilcost = sd.get_Spillage_Cost(hydro)
reserlevh = sd.get_Storage_lev(SDDP_lev,hydro)
#Scaled Inflows
path = "../../../Dispa-LINK/Outputs/SDDP/Database/Scaled_Inflows"
os.makedirs(path)
ScaledInflows = sd.get_Scaled_inflows(InflowsSDDP,hydro)

#Outputs
alertlev.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/AlertLevel.csv', header=True, index=True)
finaldemand.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Demand.csv') 
ntc.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/NTC.csv')
Outages.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Outages.csv')
PowerPlantData.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/PowerPlantData.csv') 
RenewablesAF.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/RenewablesAF.csv')
Spilcost.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Spillage_cost.csv')
reserlevh.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/StorageLevel.csv', header=True, index=True)
for year in range(1979, 2022):
    ScaledInflows.loc[str(year)].to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Scaled_Inflows/' + str(year) + '.csv')