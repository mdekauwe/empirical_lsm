#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File: evaluation.py
Author: ned haughton
Email: ned@nedhaughton.com
Github:
Description: PALS-style model evaluation
"""

import pandas as pd
import glob
import os

from pals_utils.data import pals_site_name
from pals_utils.stats import run_metrics

from .utils import print_good


# Evaluate

def evaluate_simulation(sim_data, flux_data, name):
    """Top-level simulation evaluator.

    Compares sim_data to flux_data, using standard metrics.

    TODO: Maybe get model model_name from sim_data directly (this is a PITA at
          the moment, most models don't report it).
    """
    site = pals_site_name(flux_data)
    print_good('Evaluating data for {n} at {s}'.format(n=name, s=site))

    flux_vars = ['Qle', 'Qh', 'NEE']
    eval_vars = list(set(flux_vars).intersection(sim_data.data_vars)
                                   .intersection(flux_data.data_vars))

    metric_data = pd.DataFrame()
    metric_data.index.name = 'metric'
    for v in eval_vars:
        sim_v = sim_data[v].values.ravel()
        obs_v = flux_data[v].values.ravel()

        for m, val in run_metrics(sim_v, obs_v).items():
            metric_data.ix[m, v] = val

    eval_dir = 'source/models/{n}/metrics/'.format(n=name)
    os.makedirs(eval_dir, exist_ok=True)
    eval_path = '{d}/{n}_{s}_metrics.csv'.format(d=eval_dir, n=name, s=site)
    metric_data.to_csv(eval_path)

    return metric_data


def load_sim_evaluation(name, site):
    """Load an evaluation saved from evaluate_simulation.

    :name: model name
    :site: PALS site name
    :returns: pandas dataframe with metrics
    """
    eval_path = 'source/models/{n}/metrics/{n}_{s}_metrics.csv'.format(n=name, s=site)
    metric_data = pd.DataFrame.from_csv(eval_path)

    return metric_data


def get_metric_df(models, sites):
    """Gets a DF of models metrics at the given sites (pre-computed evaluations)

    :models: TODO
    :sites: TODO
    :returns: TODO

    """
    metric_df = []
    for m in models:
        for s in sites:
            try:
                df = (pd.read_csv('source/models/{m}/metrics/{m}_{s}_metrics.csv'.format(m=m, s=s)))
                df['site'] = s
                df['name'] = m
                df = df.set_index(['name', 'site', 'metric']).stack().to_frame()
                df.index.names = ['name', 'site', 'metric', 'variable']
                df.columns = ['value']
                metric_df.append(df)
            except Exception:
                print('skipping {m} at {s}'.format(m=m, s=s))

    metric_df = pd.concat(metric_df).reset_index()

    return metric_df


def get_metric_data(names):
    """Get a dataframe of metric means for each model

    :names: List of models to grab data from
    :returns: All metric data as a pandas dataframe

    """
    import re
    import pandas as pd

    pat = re.compile('[^\W_]+(?=_metrics.csv$)')

    data = []

    for name in names:
        model_dir = 'source/models/' + name
        csv_files = glob.glob(model_dir + '/metrics/*csv')
        if len(csv_files) == 0:
            continue
        model_dfs = []
        for csvf in csv_files:
            site = re.search(pat, csvf).group(0)
            df = pd.DataFrame.from_csv(csvf)
            df['site'] = site
            model_dfs.append(df)
        model_df = pd.concat(model_dfs)
        model_df['name'] = name
        data.append(model_df)
    data = pd.concat(data)

    return data
