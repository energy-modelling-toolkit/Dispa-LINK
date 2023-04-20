"""
This script generates the cost of Spillage time series for Dispa-SET
Input : chidrobo.csv
Output : Database/Spillage_cost.csv

@authors:
                Alizon Huallpara, UMSS
                Matija Pavičević, KU Leuven

@supervision:
                Sylvain Quoilin, KU Leuven, ULiege

"""

import pandas as pd
import numpy as np

# Database import
hydro = pd.read_csv('../../../Dispa-LINK/Inputs/SDDP/chidrobo.csv', header=0, usecols=['...Nombre...', '.FPMed.', 'C.Vert.'])
hydro.set_index("...Nombre...",drop=True,inplace=True)

# Units conversion to dolars/MWh 
hydro= pd.DataFrame(hydro["C.Vert."]/hydro['.FPMed.']*3.6).T

hydro = pd.DataFrame(1,index=pd.date_range(start='2025-12-31 23:00:00+00:00', end='2026-12-31 23:00:00+00:00', freq='H'),columns=hydro.columns)*hydro.loc[0,:]
hydro.replace([np.inf, -np.inf], 0, inplace=True)

hydro.to_csv('../../../Dispa-LINK/Outputs/SDDP/Database/Spillage_cost.csv')