import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import energyscope as es
import dispaset as ds
from ..common import *
from ..search import *
from ..constants import *

def plot_convergence(LostLoad, ShedLoad, Curtailment, Error, iterations, nrows=6, ncols=1, figsize = (10, 15),
                     gridspec_kw={'height_ratios': [1, 1, 1, 1, 1, 1]}, save_path='', curtailment=False):

    data_ens_curt = pd.DataFrame(index=['LostLoad', 'ShedLoad', 'Curtailment'], columns=iterations)
    data_ens_curt.loc['LostLoad', :] = LostLoad.sum(axis=0) / 1e6  # to TWh
    data_ens_curt.loc['ShedLoad', :] = ShedLoad.sum(axis=0) / 1e6  # to TWh
    data_ens_curt.loc['Curtailment', :] = Curtailment.sum(axis=0) / 1e6  # to TWh

    data_ens_curt_max = pd.DataFrame(index=['LostLoad', 'ShedLoad', 'Curtailment'], columns=iterations)
    data_ens_curt_max.loc['LostLoad', :] = LostLoad.max(axis=0) / 1e3  # to GW
    data_ens_curt_max.loc['ShedLoad', :] = ShedLoad.max(axis=0) / 1e3  # to GW
    data_ens_curt_max.loc['Curtailment', :] = Curtailment.max(axis=0) / 1e3  # to GW

    a = LostLoad != 0
    b = ShedLoad != 0
    c = Curtailment != 0
    LostLoad_cum = LostLoad.cumsum().where(a).ffill().fillna(0) - LostLoad.cumsum().where(~a).ffill().fillna(0)
    ShedLoad_cum = ShedLoad.cumsum().where(b).ffill().fillna(0) - ShedLoad.cumsum().where(~b).ffill().fillna(0)
    Curtailment_cum = Curtailment.cumsum().where(c).ffill().fillna(0) - Curtailment.cumsum().where(~c).ffill().fillna(0)
    data_ens_curt_cons = pd.DataFrame(index=['LostLoad', 'ShedLoad', 'Curtailment'], columns=iterations)
    data_ens_curt_cons.loc['LostLoad', :] = LostLoad_cum.max(axis=0) / 1e6  # to TWh
    data_ens_curt_cons.loc['ShedLoad', :] = ShedLoad_cum.max(axis=0) / 1e6  # to TWh
    data_ens_curt_cons.loc['Curtailment', :] = Curtailment_cum.max(axis=0) / 1e6  # to TWh

    data_ens_curt_count = pd.DataFrame(index=['LostLoad', 'ShedLoad', 'Curtailment'], columns=iterations)
    data_ens_curt_count.loc['LostLoad', :] = a.sum(axis=0)
    data_ens_curt_count.loc['ShedLoad', :] = b.sum(axis=0)
    data_ens_curt_count.loc['Curtailment', :] = c.sum(axis=0)

    a_cum = a.cumsum().where(a).ffill().fillna(0) - a.cumsum().where(~a).ffill().fillna(0)
    b_cum = b.cumsum().where(b).ffill().fillna(0) - b.cumsum().where(~b).ffill().fillna(0)
    c_cum = c.cumsum().where(c).ffill().fillna(0) - c.cumsum().where(~c).ffill().fillna(0)

    data_ens_curt_cum_count = pd.DataFrame(index=['LostLoad', 'ShedLoad', 'Curtailment'], columns=iterations)
    data_ens_curt_cum_count.loc['LostLoad', :] = a_cum.max(axis=0)
    data_ens_curt_cum_count.loc['ShedLoad', :] = b_cum.max(axis=0)
    data_ens_curt_cum_count.loc['Curtailment', :] = c_cum.max(axis=0)

    all_colors = {'LostLoad': 'orange',
                  'ShedLoad': 'green',
                  'Curtailment': 'red'}
    colors1 = [all_colors[tech] for tech in data_ens_curt.loc[['ShedLoad', 'LostLoad']].T.columns]
    colors2 = [all_colors[tech] for tech in data_ens_curt.loc[['Curtailment']].T.columns]
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex=True, figsize=figsize, frameon=True,
                             gridspec_kw=gridspec_kw)
    fig.suptitle('Bi-directional soft-linking summary', fontsize=15)
    data_ens_curt.loc[['ShedLoad', 'LostLoad']].T.plot(ax=axes[0], width=0.8, kind='bar', stacked=True, color=colors1,
                                                       alpha=0.8, legend='reverse',
                                                       title='Total Energy Not Served / Curtailed', ylabel='TWh')
    data_ens_curt_max.loc[['ShedLoad', 'LostLoad']].T.plot(ax=axes[2], width=0.8, kind='bar', stacked=True, color=colors1,
                                                           alpha=0.8, legend=None,
                                                           title='Maximum Energy Not Served / Curtailed', ylabel='GW')

    data_ens_curt_cons.loc[['ShedLoad', 'LostLoad']].T.plot(ax=axes[1], width=0.8, kind='bar', stacked=True, color=colors1,
                                                            alpha=0.8, legend=None,
                                                            title='Maximum Consecutive Energy Not Served / Curtailed',
                                                            ylabel='TWh')

    data_ens_curt_count.loc[['ShedLoad', 'LostLoad']].T.plot(ax=axes[3], width=0.8, kind='bar', stacked=True, color=colors1,
                                                             alpha=0.8, legend=None,
                                                             title='Total Hours Energy Not Served / Curtailed', ylabel='h')

    data_ens_curt_cum_count.loc[['ShedLoad', 'LostLoad']].T.plot(ax=axes[4], width=0.8, kind='bar', stacked=True,
                                                                 color=colors1, alpha=0.8, legend=None,
                                                                 title='Maximum Cumulative Hours Energy Not Served / Curtailed',
                                                                 ylabel='h')
    if curtailment is True:
        data_ens_curt.loc[['Curtailment']].T.plot(ax=axes[0], color=colors2, linestyle='None', markersize=10.0, marker='o')
        data_ens_curt_max.loc[['Curtailment']].T.plot(ax=axes[2], color=colors2, linestyle='None', markersize=10.0, marker='o',
                                                      legend=None)
        data_ens_curt_cons.loc[['Curtailment']].T.plot(ax=axes[1], color=colors2, linestyle='None', markersize=10.0, marker='o',
                                                       legend=None)
        data_ens_curt_count.loc[['Curtailment']].T.plot(ax=axes[3], color=colors2, linestyle='None', markersize=10.0,
                                                        marker='o', legend=None)
        data_ens_curt_cum_count.loc[['Curtailment']].T.plot(ax=axes[4], color=colors2, linestyle='None', markersize=10.0,
                                                            marker='o', legend=None)

    Error.max().T.plot(ax=axes[5], width=0.8, kind='bar', stacked=True, color='red', alpha=0.8, legend=None,
                       title='Optimization error - check', ylabel='-')
    plt.tight_layout()
    fig.align_ylabels()
    plt.show()
    fig.savefig(save_path)
    return data_ens_curt, data_ens_curt_max, data_ens_curt_cons, data_ens_curt_count, data_ens_curt_cum_count

def plot_rug(df_series, on_off=False, cmap='Greys', fig_title='', fig_width=10, normalized=False):
    """Create multiaxis rug plot from pandas Dataframe

    Arguments:
        df_series (pd.DataFrame): 2D pandas with timed index
        on_off (bool): if True all points that are above 0 will be plotted as one color. If False all values will be colored based on their value.
        cmap (str): colormap name (from colorbrewer, matplotlib etc.)
        fig_title (str): Figure title
        normalized (bool): if True, all series colormaps will be normalized based on the maximum value of the dataframe
    Returns:
        plot
    """

    def format_axis(iax):
        # Formatting: remove all lines (not so elegant)
        for spine in ['top', 'right', 'left', 'bottom']:
            iax.axes.spines[spine].set_visible(False)
            # iax.spines['right'].set_visible(False)

        # iax.xaxis.set_ticks_position('none')
        iax.yaxis.set_ticks_position('none')
        iax.get_yaxis().set_ticks([])
        iax.yaxis.set_label_coords(-.05, -.1)

    def flag_operation(v):
        if np.isnan(v) or v == 0:
            return False
        else:
            return True

    # check if Series or dataframe
    if isinstance(df_series, pd.DataFrame):
        rows = len(df_series.columns)
    elif isinstance(df_series, pd.Series):
        df_series = df_series.to_frame()
        rows = 1
    else:
        raise ValueError("Has to be either Series or Dataframe")
    if len(df_series) < 1:
        raise ValueError("Has to be non empty Series or Dataframe")

    max_color = np.nanmax(df_series.values)
    min_color = np.nanmin(df_series.values)

    __, axes = plt.subplots(nrows=rows, ncols=1, sharex=True,
                            figsize=(fig_width, 0.35 * rows), squeeze=False,
                            frameon=False, gridspec_kw={'hspace': 0.15})

    for (item, iseries), iax in zip(df_series.iteritems(), axes.ravel()):
        format_axis(iax)
        iax.set_ylabel(str(item)[:30], rotation='horizontal',
                       rotation_mode='anchor',
                       horizontalalignment='right', x=-0.01)
        x = iseries.index

        if iseries.sum() > 0:  # if series is not empty
            if on_off:
                i_on_off = iseries.apply(flag_operation).replace(False, np.nan)
                i_on_off.plot(ax=iax, style='|', lw=.7, cmap=cmap)
            else:
                y = np.ones(len(iseries))
                # Define (truncated) colormap:
                if not normalized:  # Replace max_color (frame) with series max
                    max_color = np.nanmax(iseries.values)
                    min_color = np.nanmin(iseries.values)
                # Hack to plot max color when all series are equal
                if np.isclose(min_color, max_color):
                    min_color = min_color * 0.99

                iax.scatter(x, y,
                            marker='|', s=100,
                            c=iseries.values,
                            vmin=min_color,
                            vmax=max_color,
                            cmap=cmap)

    axes.ravel()[0].set_title(fig_title)
    axes.ravel()[-1].spines['bottom'].set_visible(True)
    axes.ravel()[-1].set_xlim(np.min(x), np.max(x))
    plt.show()


def plot_storage(es_outputs, max_loops, td_df, inputs, results, save_path=''):
    el_layers = pd.DataFrame()
    low_t_dhn_layers = pd.DataFrame()
    es_seasonal_storage_dhn = pd.DataFrame()
    es_seasonal_storage_h2 = pd.DataFrame()
    es_seasonal_storage_phs = pd.DataFrame()
    ds_seasonal_storage_dhn = pd.DataFrame()
    ds_seasonal_storage_h2 = pd.DataFrame()
    es_seasonal_storage_dhn_chdch = pd.DataFrame()
    ds_seasonal_storage_dhn_chdch = pd.DataFrame()
    es_storage_phs = pd.DataFrame()
    ds_storage_phs = pd.DataFrame()
    for i in range(max_loops):
        el_layers.loc[:, i] = es.from_td_to_year(es_outputs[i]['electricity_layers'].dropna(axis=1),
                                                 td_df.rename({'TD': 'TD_number', 'hour': 'H_of_D'},
                                                              axis=1)).sum() / 1000
        low_t_dhn_layers = es.from_td_to_year(es_outputs[i]['low_t_dhn_Layers'],
                                              td_df.rename({'TD': 'TD_number', 'hour': 'H_of_D'}, axis=1))
        es_seasonal_storage_dhn.loc[:, i] = es_outputs[i]['energy_stored']['TS_DHN_SEASONAL'] / \
                                            es_outputs[i]['assets'].loc[
                                                'TS_DHN_SEASONAL', 'f']
        es_seasonal_storage_h2.loc[:, i] = es_outputs[i]['energy_stored']['H2_STORAGE'] / es_outputs[i]['assets'].loc[
            'H2_STORAGE', 'f']
        ds_seasonal_storage_dhn.loc[:, i] = results[i]['OutputSectorXStorageLevel']['ES_DHN']
        ds_seasonal_storage_h2.loc[:, i] = results[i]['OutputSectorXStorageLevel']['ES_H2']
        es_seasonal_storage_dhn_chdch = low_t_dhn_layers.loc[:, ['TS_DHN_SEASONAL_Pin', 'TS_DHN_SEASONAL_Pout']]
        ds_seasonal_storage_dhn_chdch = results[i]['OutputSectorXStorageInput']
        es_storage_phs.loc[:, i] = es_outputs[i]['energy_stored']['PHS'] / es_outputs[i]['assets'].loc['PHS', 'f']
        ds_storage_phs.loc[:, i] = results[i]['OutputStorageLevel']['[8] - ES_PHS']

    es_seasonal_storage_dhn.set_index(ds_seasonal_storage_dhn.index, inplace=True)
    es_seasonal_storage_h2.set_index(ds_seasonal_storage_dhn.index, inplace=True)
    es_seasonal_storage_dhn_chdch.set_index(ds_seasonal_storage_dhn.index, inplace=True)
    es_storage_phs.set_index(ds_seasonal_storage_dhn.index, inplace=True)

    seasonal_storage_dhn = {}
    seasonal_storage_h2 = {}
    storage_phs = {}
    for i in range(max_loops):
        seasonal_storage_dhn[i] = pd.concat([es_seasonal_storage_dhn.loc[:, i], ds_seasonal_storage_dhn.loc[:, i]],
                                            axis=1)
        seasonal_storage_dhn[i].columns = ['ES', 'DS']
        seasonal_storage_h2[i] = pd.concat([es_seasonal_storage_h2.loc[:, i], ds_seasonal_storage_h2.loc[:, i]], axis=1)
        seasonal_storage_h2[i].columns = ['ES', 'DS']
        storage_phs[i] = pd.concat([es_storage_phs.loc[:, i], ds_storage_phs.loc[:, i]], axis=1)
        storage_phs[i].columns = ['ES', 'DS']

    res_availability = inputs[0]['param_df']['AvailabilityFactor'].loc[:, ['[5] - ES_HYDRO_RIVER', '[9] - ES_PV',
                                                                           '[11] - ES_WIND_OFFSHORE',
                                                                           '[12] - ES_WIND_ONSHORE']]
    res_availability = res_availability * inputs[0]['units'].loc[:, 'PowerCapacity']
    res_availability.dropna(axis=1, inplace=True)

    availability = pd.DataFrame()
    availability.loc[:, 'WIN'] = res_availability.loc[:, ['[11] - ES_WIND_OFFSHORE', '[12] - ES_WIND_ONSHORE']].sum(
        axis=1)
    availability.loc[:, 'SUN'] = res_availability.loc[:, ['[9] - ES_PV']]
    availability.loc[:, 'WAT'] = res_availability.loc[:, ['[5] - ES_HYDRO_RIVER']]

    capacity = inputs[0]['units'].loc[['[5] - ES_HYDRO_RIVER', '[9] - ES_PV',
                                       '[11] - ES_WIND_OFFSHORE', '[12] - ES_WIND_ONSHORE'], 'PowerCapacity']

    total_availability = availability.sum(axis=1) / capacity.sum()
    rolling = total_availability.rolling(24, min_periods=1).mean()
    dunkelflaute_1 = 0.05
    dunkelflaute_2 = 0.10
    dunkelflaute_3 = 0.15

    dunkel1 = pd.DataFrame(rolling.between(0, dunkelflaute_1).astype('int'))
    dunkel2 = pd.DataFrame(rolling.between(dunkelflaute_1, dunkelflaute_2).astype('int'))
    dunkel3 = pd.DataFrame(rolling.between(dunkelflaute_2, dunkelflaute_3).astype('int'))

    # Initialize figure and axis
    fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(8, 8))

    for j in range(4):
        i = max_loops - 1
        if j == 0:
            seasonal_storage = seasonal_storage_dhn
        elif j == 1:
            seasonal_storage = seasonal_storage_h2
        elif j == 2:
            seasonal_storage = storage_phs
        if j < 4 - 1:
            # Plot lines
            ax[j].plot(seasonal_storage[i].index, seasonal_storage[i].loc[:, 'ES'], color="black", linewidth=0.5,
                       label='EnergyScope')
            ax[j].plot(seasonal_storage[i].index, seasonal_storage[i].loc[:, 'DS'], color="blue", linewidth=0.5,
                       label='Dispa-SET')
            # Fill area when income > expenses with green
            ax[j].fill_between(
                seasonal_storage[i].index, seasonal_storage[i].loc[:, 'ES'], seasonal_storage[i].loc[:, 'DS'],
                where=(seasonal_storage[i].loc[:, 'ES'] > seasonal_storage[i].loc[:, 'DS']),
                interpolate=True, color="green", alpha=0.25, label="Overestimation")

            # Fill area when income <= expenses with red
            ax[j].fill_between(
                seasonal_storage[i].index, seasonal_storage[i].loc[:, 'ES'], seasonal_storage[i].loc[:, 'DS'],
                where=(seasonal_storage[i].loc[:, 'ES'] < seasonal_storage[i].loc[:, 'DS']),
                interpolate=True, color="red", alpha=0.25,
                label="Underestimation"
            )
            ax[j].set(ylabel='State of the charge [-]')

        else:
            ax[j].plot(seasonal_storage[i].index, total_availability.values, color="black", linestyle='dashed',
                       label='VRES availability', alpha=0.9, linewidth=0.5)
            ax[j].axhline(y=dunkelflaute_1, color='red', alpha=0.9, linewidth=0.7)
            ax[j].axhline(y=dunkelflaute_2, color='orange', alpha=0.9, linewidth=0.7)
            ax[j].axhline(y=dunkelflaute_3, color='gold', alpha=0.9, linewidth=0.7)
            ax[j].set(ylabel='Availability [-]')
            ax[j].fill_between(seasonal_storage[i].index, dunkel3.loc[:, 0], 0, where=(dunkel3.loc[:, 0] > 0),
                               interpolate=False, color="gold", alpha=0.9,
                               label="Low < " + str(dunkelflaute_3 * 100) + "%")
            ax[j].fill_between(seasonal_storage[i].index, dunkel2.loc[:, 0], 0, where=(dunkel2.loc[:, 0] > 0),
                               interpolate=False, color="orange", alpha=0.9,
                               label="Critical < " + str(dunkelflaute_2 * 100) + "%")
            ax[j].fill_between(seasonal_storage[i].index, dunkel1.loc[:, 0], 0, where=(dunkel1.loc[:, 0] > 0),
                               interpolate=False, color="red", alpha=0.9,
                               label="Extreme < " + str(dunkelflaute_1 * 100) + "%")

            ax[j].set_ylim(top=1)

        if j == 0:
            title = 'DHN Storage'
        elif j == 1:
            title = 'H2 Storage'
        elif j == 2:
            title = 'PHS Storage'
        else:
            title = 'VRES Availability'
        ax[j].set_title(title)

    handles, labels = ax[0].get_legend_handles_labels()
    handles1, labels1 = ax[j].get_legend_handles_labels()
    fig.legend(handles=handles + handles1, loc="lower left", mode="expand", ncol=4)
    fig.align_ylabels()
    plt.subplots_adjust(left=0.12, bottom=0.1, right=0.9, top=0.95, wspace=0.2, hspace=0.2)
    plt.show()

    fig.savefig(save_path)


def plot_capacity_energy_mix(inputs, results, es_outputs, ShedLoad, LostLoad, max_loops, save_path=''):
    r = {}
    DS_generation = pd.DataFrame()
    ES_generation = pd.DataFrame()
    for i in range(max_loops):
        r[i] = ds.get_result_analysis(inputs[i], results[i])
        r[i]['FuelData']['Non-CHP']['Generation [TWh]'].loc['WAT', 'HPHS'] = 0
        DS_generation.loc[:, i] = r[i]['FuelData']['Non-CHP']['Generation [TWh]'].sum(axis=1)
        DS_generation.loc['ENSX', i] = results[i]['OutputXNotServed'].sum().sum() / 1e6

        es_generation = pd.DataFrame(es_outputs[i]['year_balance']['ELECTRICITY'])
        es_generation['Fuel'] = es_generation.index.map(mapping['ES']['FUEL'])
        es_generation['Sort'] = es_generation.index.map(mapping['ES']['SORT'])
        es_generation.loc['BIO_HYDROLYSIS', ['Fuel', 'Sort']] = ['BIO', 'ELEC']
        ES_generation.loc[:, i] = es_generation.loc[es_generation['Sort'] == 'ELEC'].groupby(by=['Fuel']).sum()

    DS_generation.loc['OTH', :] = 0
    DS_generation.loc['ENS', :] = ShedLoad.sum().values / 1e6 + LostLoad.sum().values / 1e6
    ES_generation = pd.DataFrame(ES_generation, index=DS_generation.index).fillna(0) / 1000

    # # Bar plot with the installed capacities in all countries:
    cap = pd.DataFrame()
    for i in range(max_loops):
        cap.loc[:, i] = ds.plot_zone_capacities(inputs[i], results[i], plot=False)['PowerCapacity'].T / 1e3

    colors = {'LIG': '#af4b9180',
              'PEA': '#af4b9199',
              'HRD': 'darkviolet',
              'OIL': 'magenta',
              'GAS': '#d7642dff',
              'NUC': '#466eb4ff',
              'SUN': '#e6a532ff',
              'WIN': '#41afaaff',
              'WAT': '#00a0e1ff',
              'HYD': '#A0522D',
              'BIO': '#7daf4bff',
              'AMO': '#ffff00ff',
              'GEO': '#7daf4bbf',
              'Storage': '#b93c46ff',
              'FlowIn': 'red',
              'FlowOut': 'green',
              # 'FlowIn': '#b93c46b2',
              # 'FlowOut': '#b93c4666',
              'OTH': '#57D53B',
              'WST': '#b9c337ff',
              'HDAM': '#00a0e1ff',
              'HPHS': 'blue',
              'THMS': '#C04000ff',
              'BATS': '#41A317ff',
              'BEVS': '#b9c33799',
              'SCSP': '#e6a532ff',
              'P2GS': '#A0522D',
              'ShedLoad': '#ffffffff',
              'AIR': '#aed6f1ff',
              'WHT': '#a93226ff',
              'ELE': '#2C75FFff',
              'THE': '#c70509ff',
              'HeatSlack': '#943126ff',
              'ENS': 'red',
              'ENSX': 'darkred'
              }

    iterations = {0: 'Initialization', 1: 'Reserve', 2: 'Iter1', 3: 'Iter2', 4: 'Iter3'}
    ES_generation.rename(columns=iterations, inplace=True)
    DS_generation.rename(columns=iterations, inplace=True)
    cap.rename(columns=iterations, inplace=True)
    cap.loc['ENS', :] = np.nan
    cap.loc['ENSX', :] = np.nan

    figsize = (8, 8)
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, figsize=figsize, frameon=True,  # 14 4*2
                           gridspec_kw={'height_ratios': [1, 1]})
    ES_generation.T.plot.bar(stacked=True, width=0.35, position=1.02, color=colors, ax=ax[1], alpha=0.7,
                             edgecolor="gray")
    DS_generation.T.plot.bar(stacked=True, width=0.35, position=-0.02, color=colors, ax=ax[1], alpha=0.7,
                             edgecolor="gray")
    ax[1].set_ylabel('Energy [TWh]')
    ax[0].set_ylabel('Capacity [GW]')
    ax[0].set_title('Total Installed Capacity')
    ax[1].set_title('Total Energy Output from EnergyScope (left) and Dispa-SET (right)')
    cap.T.plot.bar(stacked=True, width=0.35, color=colors, ax=ax[0], alpha=0.7, edgecolor="gray")
    fig.align_ylabels()
    ax[0].get_legend().remove()
    handles, labels = ax[0].get_legend_handles_labels()
    for i in [0, 1]:
        threshold = 10
        for c in ax[i].containers:
            labels = [f'{v:.0f}' if v > threshold else "" for v in c.datavalues]
            ax[i].bar_label(c, labels=labels, label_type="center")
    plt.legend(title='Fuel', handles=handles[::-1], loc=4, bbox_to_anchor=(1.2, 0.5))
    plt.xticks(rotation=0)
    plt.subplots_adjust(left=0.12, bottom=0.1, right=0.85, top=0.95, wspace=0.2, hspace=0.2)
    plt.show()
    fig.savefig(save_path)

