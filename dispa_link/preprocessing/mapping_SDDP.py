import pandas as pd
import numpy as np

def get_blocks_to_hours(start_date='2021-12-31 23:00:00+00:00', end_date='2026-12-31 23:00:00+00:00'):

    df_t = pd.DataFrame()
    df_t['Datetime'] = pd.date_range(start=start_date, end=end_date, freq='H')
    df_t = df_t.assign(Weekday=df_t['Datetime'].dt.weekday, Hour=pd.DatetimeIndex(df_t.Datetime).hour, Year=df_t['Datetime'].dt.isocalendar().year.astype('int32'), Week=df_t['Datetime'].dt.isocalendar().week.astype('int32'))
    df_t['Block'] = " "


    # data_merge = data_merge.assign(Weekday=data_merge['Datetime'].dt.weekday, Week=data_merge['Datetime'].dt.isocalendar().week, Year=data_merge['Datetime'].dt.isocalendar().year)
    
    condiciones =[
        # lunes
        (df_t['Weekday'] == 0) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 0) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 0) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 0) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 0) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 0) & (df_t['Hour'] == 22),
        (df_t['Weekday'] == 0) & (df_t['Hour'] >= 20) & (df_t['Hour'] <= 21),
        # martes
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 1) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 1) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 22),
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 20),
        (df_t['Weekday'] == 1) & (df_t['Hour'] == 21),
        # miercoles
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 2) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 2) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 22),
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 20),
        (df_t['Weekday'] == 2) & (df_t['Hour'] == 21),
        # jueves
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 3) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 3) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 22),
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 20),
        (df_t['Weekday'] == 3) & (df_t['Hour'] == 21),
        # viernes
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 4) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 4) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 22),
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 20),
        (df_t['Weekday'] == 4) & (df_t['Hour'] == 21),
        # sabado
        (df_t['Weekday'] == 5) & (df_t['Hour'] == 0),
        (df_t['Weekday'] == 5) & (df_t['Hour'] == 23),
        (df_t['Weekday'] == 5) & (df_t['Hour'] >= 8) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 5) & (df_t['Hour'] >= 1) & (df_t['Hour'] <= 7),
        (df_t['Weekday'] == 5) & (df_t['Hour'] >= 19) & (df_t['Hour'] <= 22),

        # domingo
        (df_t['Weekday'] == 6) & (df_t['Hour'] >= 0) & (df_t['Hour'] <= 18),
        (df_t['Weekday'] == 6) & (df_t['Hour'] == 19),
        (df_t['Weekday'] == 6) & (df_t['Hour'] >= 20) & (df_t['Hour'] <= 21),
        (df_t['Weekday'] == 6) & (df_t['Hour'] >= 22) & (df_t['Hour'] <= 23)
    ]

    opciones = [4, 4, 4, 5, 3, 3, 2,
                4, 4, 4, 5, 3, 3, 1, 2,
                4, 4, 4, 5, 3, 3, 1, 2,
                4, 4, 4, 5, 3, 3, 1, 2,
                4, 4, 4, 5, 3, 3, 1, 2,
                4, 4, 4, 5, 3,
                5, 4, 3, 4
                ]

    df_t['Block'] = np.select(condiciones,opciones)
    # df_t = df_t.drop(['Hour','Weekday'], axis=1)

    return df_t