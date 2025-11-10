# -*- encoding:utf-8 -*-
"""
Pandas helper functions for rolling, expanding, and resampling operations.
"""
from __future__ import absolute_import

import pandas as pd
import numpy as np

# Rolling functions
def pd_rolling_mean(series, window):
    return series.rolling(window=window).mean()

def pd_rolling_std(series, window):
    return series.rolling(window=window).std()

def pd_rolling_var(series, window):
    return series.rolling(window=window).var()

def pd_rolling_median(series, window):
    return series.rolling(window=window).median()

def pd_rolling_max(series, window):
    return series.rolling(window=window).max()

def pd_rolling_min(series, window):
    return series.rolling(window=window).min()

def pd_rolling_corr(series1, series2, window):
    return series1.rolling(window=window).corr(series2)

def pd_rolling_cov(series1, series2, window):
    return series1.rolling(window=window).cov(series2)

def pd_rolling_sum(series, window):
    return series.rolling(window=window).sum()

def pd_rolling_kurt(series, window):
    return series.rolling(window=window).kurt()

def pd_rolling_skew(series, window):
    return series.rolling(window=window).skew()

# EWM (Exponentially Weighted Moving) functions
def pd_ewm_mean(series, span):
    return series.ewm(span=span).mean()

def pd_ewm_corr(series1, series2, span):
    return series1.ewm(span=span).corr(series2)

def pd_ewm_std(series, span):
    return series.ewm(span=span).std()

def pd_ewm_cov(series1, series2, span):
    return series1.ewm(span=span).cov(series2)

def pd_ewm_var(series, span):
    return series.ewm(span=span).var()

# Expanding functions
def pd_expanding_mean(series):
    return series.expanding().mean()

def pd_expanding_std(series):
    return series.expanding().std()

def pd_expanding_var(series):
    return series.expanding().var()

def pd_expanding_median(series):
    return series.expanding().median()

def pd_expanding_max(series):
    return series.expanding().max()

def pd_expanding_min(series):
    return series.expanding().min()

def pd_expanding_corr(series1, series2):
    return series1.expanding().corr(series2)

def pd_expanding_cov(series1, series2):
    return series1.expanding().cov(series2)

def pd_expanding_sum(series):
    return series.expanding().sum()

def pd_expanding_kurt(series):
    return series.expanding().kurt()

def pd_expanding_skew(series):
    return series.expanding().skew()

# Resample function
def pd_resample(series, rule):
    return series.resample(rule)

__all__ = [
    'pd_rolling_mean', 'pd_rolling_std', 'pd_rolling_var', 'pd_rolling_median',
    'pd_rolling_max', 'pd_rolling_min', 'pd_rolling_corr', 'pd_rolling_cov',
    'pd_rolling_sum', 'pd_rolling_kurt', 'pd_rolling_skew',
    'pd_ewm_mean', 'pd_ewm_corr', 'pd_ewm_std', 'pd_ewm_cov', 'pd_ewm_var',
    'pd_expanding_mean', 'pd_expanding_std', 'pd_expanding_var', 'pd_expanding_median',
    'pd_expanding_max', 'pd_expanding_min', 'pd_expanding_corr', 'pd_expanding_cov',
    'pd_expanding_sum', 'pd_expanding_kurt', 'pd_expanding_skew',
    'pd_resample'
]

