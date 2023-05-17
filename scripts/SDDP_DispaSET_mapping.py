# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 16:02:04 2023

@author: UMSS
"""
import dispa_link as dl
import pandas as pd
import numpy as np
import os

###User's inputs
# folder path of SDDP database
folder_path = "C:/Users/UMSS/Documents/Dispa-LINK/Database/SDDP/pmp_sddp_08032022"

# Simulation time range
start_date, end_date = '2025-12-31 23:00:00+00:00', '2026-12-31 23:00:00+00:00'

# Transfer lines between zones

lines = {'SU -> CE': ['POT-115 -> OCU-115','SUC-230 -> SAN-230','SUC-230 -> MIZ-230'],
       'CE -> SU': ['OCU-115 -> POT-115','SAN-230 -> SUC-230','MIZ-230 -> SUC-230'],
       'CE -> OR': ['CAR-230 -> YAP-230','CAR-230 -> ARB-230','CAR-500 -> BRE-500'],
       'OR -> CE': ['YAP-230 -> CAR-230','ARB-230 -> CAR-230','BRE-500 -> CAR-500'],
       'OR -> NO': ['GUA-230 -> PRA-230','GUA-230 -> PRA-(2)'],
       'NO -> OR': ['PRA-230 -> GUA-230','PRA-(2) -> GUA-230'],
       'CE -> NO': ['SAN-230 -> PCA-230','VIN-230 -> MAZ-230','SAN-230 -> MIG-230'],
       'NO -> CE': ['PCA-230 -> SAN-230','MAZ-230 -> VIN-230','MIG-230 -> SAN-230']}

#TODO: user shoudl only specify folder where SDDP database was extracted (becase datafiles are standrdized and always have the same names)

# Inputs for alert level
SDDP_alert = pd.read_csv(str(folder_path)+'/volale.csv', index_col=0, header=3)
SDDP_alert.columns = SDDP_alert.columns.str.replace(' ', '')
hydro = pd.read_csv(str(folder_path)+'/chidrobo.csv', usecols=['...Nombre...','.VMax..','.VInic.','....Pot','.FPMed.','C.Vert.','.PV.','.QMax..','..ICP..'], header=0)

#Inputs demand
SDDP_demand = pd.read_fwf(str(folder_path)+'/dbf005bo.dat', encoding='cp1252', header=0, colspecs="infer", engine='python')
dfc = pd.read_fwf(str(folder_path)+'/dcirc.dat',header=1,colspecs="infer", engine='python', encoding='cp1252')
buslist = pd.read_csv('../../Dispa-LINK/Inputs/SDDP/BusList-ZONES1.csv', encoding='cp1252')

#Inputs outages
#thermal
dft1 = pd.read_csv('../../Dispa-LINK/Inputs/SDDP/pmtrsebo.csv', encoding='cp1252')
dft2 = pd.read_csv(str(folder_path)+'/ctermibo.csv', usecols=['...Nombre...','.PotIns','.GerMax','..Teif.','Comb'])

#hydro
dfh1 = pd.read_csv('../../Dispa-LINK/Inputs/SDDP/pmhisebo.csv', encoding='cp1252')
# #vres
dfv1 = pd.read_fwf(str(folder_path)+'/cgndbo.dat', header=1, colspecs="infer", engine='python',usecols=['!Num Name........','ProbFal','.PotIns'])

dbus = pd.read_csv('../../Dispa-LINK/Inputs/SDDP/dbus.csv',encoding='cp1252', header=1, usecols= ['Name','Gen. name'])

#Renewables availability factor
vresaf = pd.read_fwf(str(folder_path)+'/blrenw005bo0_w.dat',header=1,colspecs="infer", engine='python')

#reservoirlevel
SDDP_lev = pd.read_csv(str(folder_path)+'/rvolfin.csv', encoding='cp1252', header=3)

#ScaledInflows
InflowsSDDP = pd.read_fwf(str(folder_path)+'/hinflw_w.dat', header=0, colspecs="infer", engine='python')

#Results
alertlev = dl.get_alert_level(hydro,SDDP_alert, start_date, end_date)
finaldemand = dl.get_demand(SDDP_demand, dfc, buslist, start_date, end_date)
ntc = dl.get_NTC(dfc, lines, start_date, end_date)
Outages = dl.get_Outages(hydro,dft1,dft2, dfh1,dfv1, start_date, end_date)
PowerPlantData = dl.get_Power_PlantData(hydro,dft2,dfv1,dbus,buslist)
RenewablesAF = dl.get_renewables_AF(vresaf,start_date, end_date)
Spilcost = dl.get_Spillage_Cost(hydro, start_date, end_date)
reserlevh = dl.get_Storage_lev(SDDP_lev,hydro,start_date, end_date)

#Scaled Inflows
path = "../../Dispa-LINK/Outputs/SDDP/Database/Scaled_Inflows"
os.makedirs(path)
ScaledInflows = dl.get_Scaled_inflows(InflowsSDDP,hydro)

#Outputs
alertlev.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/AlertLevel.csv', header=True, index=True)
finaldemand.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/Demand.csv') 
ntc.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/NTC.csv')
Outages.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/Outages.csv')
PowerPlantData.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/PowerPlantData.csv') 
RenewablesAF.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/RenewablesAF.csv')
Spilcost.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/Spillage_cost.csv')
reserlevh.to_csv('../../Dispa-LINK/Outputs/SDDP/Database/StorageLevel.csv', header=True, index=True)
for year in range(1979, 2022):
    ScaledInflows.loc[str(year)].to_csv('../../Dispa-LINK/Outputs/SDDP/Database/Scaled_Inflows/' + str(year) + '.csv')