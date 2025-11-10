# -*- encoding:utf-8 -*-
"""
Environment configuration and market type definitions.
"""
from __future__ import absolute_import
from enum import Enum

class EMarketSourceType(Enum):
    """Market data source types"""
    E_MARKET_SOURCE_TUSHARE = "tushare"
    E_MARKET_SOURCE_NETEASE = "netease"
    E_MARKET_SOURCE_SINA = "sina"
    E_MARKET_SOURCE_YAHOO = "yahoo"

class EMarketTargetType(Enum):
    """Target market types"""
    E_MARKET_TARGET_US = "US"
    E_MARKET_TARGET_CN = "CN"
    E_MARKET_TARGET_HK = "HK"
    E_MARKET_TARGET_TC = "TC"  # Crypto
    E_MARKET_TARGET_FUTURES_CN = "FUTURES_CN"
    E_MARKET_TARGET_FUTURES_GLOBAL = "FUTURES_GLOBAL"
    E_MARKET_TARGET_OPTIONS_US = "OPTIONS_US"

class EMarketSubType(Enum):
    """Market subtypes"""
    pass

class EMarketDataSplitMode(Enum):
    """Data split modes"""
    E_DATA_SPLIT_NORMAL = "normal"
    E_DATA_SPLIT_ADJUST = "adjust"

class EMarketDataFetchMode(Enum):
    """Data fetch modes"""
    E_DATA_FETCH_FORCE_NET = "force_net"
    E_DATA_FETCH_FORCE_LOCAL = "force_local"
    E_DATA_FETCH_LOCAL = "local"

class EDataCacheType(Enum):
    """Data cache types"""
    E_DATA_CACHE_CSV = "csv"
    E_DATA_CACHE_HDF5 = "hdf5"

# Global environment variables
g_market_target = EMarketTargetType.E_MARKET_TARGET_US
g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_LOCAL
g_is_mac_os = False
g_cpu_cnt = 4

__all__ = [
    'EMarketSourceType', 'EMarketTargetType', 'EMarketSubType',
    'EMarketDataSplitMode', 'EMarketDataFetchMode', 'EDataCacheType',
    'g_market_target', 'g_data_fetch_mode', 'g_is_mac_os', 'g_cpu_cnt'
]

