from matplotlib import dates
from termcolor import colored
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
import matplotlib.ticker as plticker
import matplotlib.ticker as ticker

import am_config as amc
from ampyutils import amutils

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

__author__ = 'amuls'


def plot_rise_set_times(gnss: str, df_rs: pd.DataFrame, logger: logging.Logger, showplot: bool = False):
    """
    plot_rise_set_times plots the rise/set times vs time per SVs as observed / predicted
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')
    logger.info('{func:s}: plotting rise/set times'.format(func=cFuncName))
    # amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=df_dt, dfName='df_dt')

    # set up the plot
    plt.style.use('ggplot')
    # plt.style.use('seaborn-darkgrid')

    # create colormap with 36 discrete colors
    max_prn = 36
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=max_prn, font_size=14)

    # subplots
    fig, ax = plt.subplots(figsize=(16.0, 10.0))
    fig.suptitle('Rise Set for system {gnss:s} on {date:s}'.format(gnss=amc.dRTK['rnx']['gnss'][gnss]['name'], date='{yy:02d}/{doy:03d}'.format(yy=amc.dRTK['rnx']['times']['yy'], doy=amc.dRTK['rnx']['times']['doy'])), fontdict=title_font, fontsize=24)

    # draw the rise to set lines per PRN
    for prn in df_rs.index:
        y_prn = int(prn[1:]) - 1

        # get the lists with rise / set times as observed
        for dt_obs_rise, dt_obs_set in zip(df_rs.loc[prn]['obs_rise'], df_rs.loc[prn]['obs_set']):
            ax.plot_date([dt_obs_rise, dt_obs_set], [y_prn, y_prn], linestyle='solid', color=prn_colors[y_prn], linewidth=2, marker='v', markersize=4, alpha=1)

        # get the lists with rise / set times by TLEs
        for dt_tle_rise, dt_tle_set, dt_tle_cul in zip(df_rs.loc[prn]['tle_rise'], df_rs.loc[prn]['tle_set'], df_rs.loc[prn]['tle_cul']):
            ax.plot_date([dt_tle_rise, dt_tle_set], [y_prn - 0.25, y_prn - 0.25], linestyle='--', color=prn_colors[y_prn], linewidth=2, marker='^', markersize=4, alpha=0.5)

            # add a indicator for the culmination time of PRN
            ax.plot(dt_tle_cul, y_prn - 0.25, marker='d', markersize=4, alpha=0.5, color=prn_colors[y_prn])

    # format the date time ticks
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d-%m-%Y'))

    ax.xaxis.set_minor_locator(dates.HourLocator(interval=3))
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))
    plt.xticks()

    # format the y-ticks to represent the PRN number
    plt.yticks(np.arange(0, max_prn))
    prn_ticks = [''] * max_prn

    # get list of observed PRN numbers (without satsyst letter)
    prn_nrs = [int(prn[1:]) for prn in df_rs.index]

    # and the corresponding ticks
    for prn_nr, prn_txt in zip(prn_nrs, df_rs.index):
        prn_ticks[prn_nr - 1] = prn_txt

    # adjust color for y ticks
    for color, tick in zip(prn_colors, ax.yaxis.get_major_ticks()):
        tick.label1.set_color(color)  # set the color property
        tick.label1.set_fontweight('bold')
    ax.set_yticklabels(prn_ticks)

    # set the axis labels
    ax.set_xlabel('Time', fontdict=title_font)
    ax.set_ylabel('PRN', fontdict=title_font)

    # save the plot in subdir png of GNSSSystem
    png_dir = os.path.join(amc.dRTK['gfzrnxDir'], amc.dRTK['rnx']['gnss'][gnss]['marker'], 'png')
    amutils.mkdir_p(png_dir)
    pngName = os.path.join(png_dir, os.path.splitext(amc.dRTK['rnx']['gnss'][gnss]['obstab'])[0] + '-RS.png')
    fig.savefig(pngName, dpi=fig.dpi)

    logger.info('{func:s}: created plot {plot:s}'.format(func=cFuncName, plot=colored(pngName, 'green')))

    if showplot:
        plt.show(block=True)
    else:
        plt.close(fig)


def plot_rise_set_stats(gnss: str, df_arcs: pd.DataFrame, logger: logging.Logger, showplot: bool = False):
    """
    plot_rise_set_stats plots the rise/set statistics per SVs
    """
    cFuncName = colored(os.path.basename(__file__), 'yellow') + ' - ' + colored(sys._getframe().f_code.co_name, 'green')
    logger.info('{func:s}: plotting observation statistics'.format(func=cFuncName))
    # amutils.logHeadTailDataFrame(logger=logger, callerName=cFuncName, df=df_dt, dfName='df_dt')

    # set up the plot
    plt.style.use('ggplot')
    # plt.style.use('seaborn-darkgrid')

    # create colormap with 36 discrete colors
    max_prn = 36
    prn_colors, title_font = amutils.create_colormap_font(nrcolors=max_prn, font_size=14)

    width = 0.2  # the width of the bars
    x = np.arange(df_arcs.shape[0])  # the label locations

    # subplots
    fig, (ax1, ax2) = plt.subplots(figsize=(14.0, 9.0), nrows=2)
    fig.suptitle('Rise Set statistics for system {gnss:s} on {date:s}'.format(gnss=amc.dRTK['rnx']['gnss'][gnss]['name'], date='{yy:02d}/{doy:03d}'.format(yy=amc.dRTK['rnx']['times']['yy'], doy=amc.dRTK['rnx']['times']['doy'])), fontdict=title_font, fontsize=24)

    # creating bar plots for absolute values
    # draw ARC0
    ax1.bar(x - 2 * width + 0.1, df_arcs['Arc0_tle'], width=0.75 * width, color='blue', alpha=0.35, edgecolor='black', hatch='//', label='TLE Arc 1')
    ax1.bar(x - 2 * width, df_arcs['Arc0_obs'], width=0.75 * width, color='blue', label='Obs Arc 1')
    # draw ARC1
    ax1.bar(x - width / 2 + 0.1, df_arcs['Arc1_tle'], width=0.75 * width, color='red', alpha=0.35, edgecolor='black', hatch='//', label='TLE Arc 2')
    ax1.bar(x - width / 2, df_arcs['Arc1_obs'], width=0.75 * width, color='red', label='Obs Arc 2')
    # draw ARC2
    ax1.bar(x + width + 0.1, df_arcs['Arc2_tle'], width=0.75 * width, color='green', alpha=0.35, edgecolor='black', hatch='//', label='TLE Arc 3')
    ax1.bar(x + width, df_arcs['Arc2_obs'], width=0.75 * width, color='green', label='Obs Arc 3')

    # beautify plot
    ax1.xaxis.grid()
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # ax1.set_xlabel('PRN', fontdict=title_font)
    ax1.set_ylabel('#Observed / #Predicted', fontdict=title_font)

    # setticks on X axis to represent the PRN
    ax1.xaxis.set_ticks(np.arange(0, df_arcs.shape[0], 1))
    ax1.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))
    ax1.set_xticklabels(df_arcs['PRN'], rotation=90)

    # # creating bar plots for relative values
    # draw ARC0
    percentages = [df_arcs.iloc[i]['Arc0_obs'] / df_arcs.iloc[i]['Arc0_tle'] * 100 for i in np.arange(df_arcs.shape[0])]
    ax2.bar(x - 2 * width, percentages, width=width * 1.2, color='blue', label='% Arc 1')
    # draw ARC1
    percentages = [df_arcs.iloc[i]['Arc1_obs'] / df_arcs.iloc[i]['Arc1_tle'] * 100 for i in np.arange(df_arcs.shape[0])]
    ax2.bar(x - width / 2, percentages, width=width * 1.2, color='red', label='% Arc 2')
    # draw ARC2
    percentages = [df_arcs.iloc[i]['Arc2_obs'] / df_arcs.iloc[i]['Arc2_tle'] * 100 if df_arcs.iloc[i]['Arc2_tle'] > 0 else np.nan for i in np.arange(df_arcs.shape[0])]
    print(percentages)
    ax2.bar(x + width, percentages, width=width * 1.2, color='green', label='% Arc 2')

    # beautify plot
    ax2.xaxis.grid()
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    ax2.set_xlabel('PRN', fontdict=title_font)
    ax2.set_ylabel('Percentage', fontdict=title_font)

    # setticks on X axis to represent the PRN
    ax2.xaxis.set_ticks(np.arange(0, df_arcs.shape[0], 1))
    ax2.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0f'))
    ax2.set_xticklabels(df_arcs['PRN'], rotation=90)

    plt.show()


def longest(a):
    return max(len(a), *map(longest, a)) if isinstance(a, list) and a else 0
