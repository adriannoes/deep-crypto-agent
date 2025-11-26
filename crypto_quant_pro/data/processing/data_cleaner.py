"""Data processing and cleaning utilities."""
import logging
from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


class DataCleaner:
    """
    Data cleaning and preprocessing utilities for market data.

    Provides methods for cleaning, validating, and preprocessing
    financial market data from various sources.
    """

    @staticmethod
    def clean_ohlcv_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean OHLCV (Open, High, Low, Close, Volume) data.

        Args:
            data: DataFrame with OHLCV columns

        Returns:
            Cleaned DataFrame
        """
        if data.empty:
            return data

        df = data.copy()

        # Ensure required columns exist
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
            return pd.DataFrame()

        # Convert to numeric types
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Remove rows with NaN values in critical columns
        df = df.dropna(subset=["open", "high", "low", "close"])

        # Validate OHLC relationships
        df = DataCleaner._validate_ohlc_relationships(df)

        # Handle volume data
        df = DataCleaner._clean_volume_data(df)

        # Remove duplicates
        df = df[~df.index.duplicated(keep="first")]

        # Sort by timestamp
        df = df.sort_index()

        return df

    @staticmethod
    def _validate_ohlc_relationships(data: pd.DataFrame) -> pd.DataFrame:
        """
        Validate OHLC price relationships.

        Args:
            data: DataFrame with OHLC columns

        Returns:
            DataFrame with validated relationships
        """
        df = data.copy()

        # High should be >= max(open, close)
        invalid_high = df["high"] < np.maximum(df["open"], df["close"])
        if invalid_high.any():
            logger.warning(f"Found {invalid_high.sum()} invalid high prices, correcting")
            df.loc[invalid_high, "high"] = np.maximum(
                df.loc[invalid_high, "open"], df.loc[invalid_high, "close"]
            )

        # Low should be <= min(open, close)
        invalid_low = df["low"] > np.minimum(df["open"], df["close"])
        if invalid_low.any():
            logger.warning(f"Found {invalid_low.sum()} invalid low prices, correcting")
            df.loc[invalid_low, "low"] = np.minimum(
                df.loc[invalid_low, "open"], df.loc[invalid_low, "close"]
            )

        return df

    @staticmethod
    def _clean_volume_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate volume data.

        Args:
            data: DataFrame with volume column

        Returns:
            DataFrame with cleaned volume data
        """
        df = data.copy()

        # Convert volume to numeric
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

        # Replace negative volumes with 0
        df.loc[df["volume"] < 0, "volume"] = 0

        # Handle NaN volumes (replace with 0 or interpolate)
        if df["volume"].isna().any():
            logger.warning("Found NaN volumes, replacing with 0")
            df["volume"] = df["volume"].fillna(0)

        return df

    @staticmethod
    def remove_outliers(
        data: pd.DataFrame,
        method: str = "iqr",
        threshold: float = 1.5,
        columns: Optional[list[str]] = None,
    ) -> pd.DataFrame:
        """
        Remove outliers from data using statistical methods.

        Args:
            data: DataFrame to clean
            method: Outlier detection method ('iqr', 'zscore', 'isolation_forest')
            threshold: Threshold for outlier detection
            columns: Columns to check for outliers (default: price columns)

        Returns:
            DataFrame with outliers removed
        """
        if data.empty:
            return data

        df = data.copy()

        if columns is None:
            columns = ["open", "high", "low", "close", "volume"]

        columns = [col for col in columns if col in df.columns]

        if not columns:
            return df

        if method == "iqr":
            return DataCleaner._remove_outliers_iqr(df, columns, threshold)
        elif method == "zscore":
            return DataCleaner._remove_outliers_zscore(df, columns, threshold)
        else:
            logger.warning(f"Unsupported outlier method: {method}")
            return df

    @staticmethod
    def _remove_outliers_iqr(
        data: pd.DataFrame, columns: list[str], threshold: float
    ) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        df = data.copy()
        mask = pd.Series(True, index=df.index)

        for col in columns:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            col_mask = (df[col] >= lower_bound) & (df[col] <= upper_bound)
            mask = mask & col_mask

        outliers_count = (~mask).sum()
        if outliers_count > 0:
            logger.info(f"Removed {outliers_count} outliers using IQR method")
            df = df[mask]

        return df

    @staticmethod
    def _remove_outliers_zscore(
        data: pd.DataFrame, columns: list[str], threshold: float
    ) -> pd.DataFrame:
        """Remove outliers using Z-score method."""
        df = data.copy()
        mask = pd.Series(True, index=df.index)

        for col in columns:
            z_scores = np.abs(stats.zscore(df[col]))
            col_mask = z_scores < threshold
            mask = mask & col_mask

        outliers_count = (~mask).sum()
        if outliers_count > 0:
            logger.info(f"Removed {outliers_count} outliers using Z-score method")
            df = df[mask]

        return df

    @staticmethod
    def fill_missing_data(
        data: pd.DataFrame, method: str = "forward_fill", columns: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """
        Fill missing data in DataFrame.

        Args:
            data: DataFrame with missing data
            method: Fill method ('forward_fill', 'backward_fill', 'interpolate', 'mean')
            columns: Columns to fill (default: all numeric columns)

        Returns:
            DataFrame with filled missing data
        """
        if data.empty:
            return data

        df = data.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        columns = [col for col in columns if col in df.columns]

        if not columns:
            return df

        if method == "forward_fill":
            df[columns] = df[columns].fillna(method="ffill")
        elif method == "backward_fill":
            df[columns] = df[columns].fillna(method="bfill")
        elif method == "interpolate":
            df[columns] = df[columns].interpolate(method="linear")
        elif method == "mean":
            for col in columns:
                df[col] = df[col].fillna(df[col].mean())
        else:
            logger.warning(f"Unsupported fill method: {method}")
            return df

        return df

    @staticmethod
    def normalize_data(
        data: pd.DataFrame, method: str = "min_max", columns: Optional[list[str]] = None
    ) -> pd.DataFrame:
        """
        Normalize data to a common scale.

        Args:
            data: DataFrame to normalize
            method: Normalization method ('min_max', 'zscore', 'robust')
            columns: Columns to normalize (default: numeric columns)

        Returns:
            Normalized DataFrame
        """
        if data.empty:
            return data

        df = data.copy()

        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        columns = [col for col in columns if col in df.columns and col != "volume"]

        if not columns:
            return df

        if method == "min_max":
            for col in columns:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
        elif method == "zscore":
            for col in columns:
                df[col] = (df[col] - df[col].mean()) / df[col].std()
        elif method == "robust":
            for col in columns:
                median = df[col].median()
                mad = (df[col] - median).abs().median()
                if mad > 0:
                    df[col] = (df[col] - median) / mad
        else:
            logger.warning(f"Unsupported normalization method: {method}")
            return df

        return df

    @staticmethod
    def resample_data(data: pd.DataFrame, timeframe: str, method: str = "last") -> pd.DataFrame:
        """
        Resample data to different timeframe.

        Args:
            data: DataFrame to resample
            timeframe: Target timeframe (e.g., '1H', '1D', '1W')
            method: Aggregation method for resampling

        Returns:
            Resampled DataFrame
        """
        if data.empty:
            return data

        df = data.copy()

        # Define aggregation functions based on method
        if method == "last":
            agg_funcs = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        elif method == "first":
            agg_funcs = {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "first",
                "volume": "sum",
            }
        else:
            logger.warning(f"Unsupported resampling method: {method}")
            return df

        # Resample data
        df_resampled = df.resample(timeframe).agg(agg_funcs)

        # Remove NaN values
        df_resampled = df_resampled.dropna()

        return df_resampled

    @staticmethod
    def validate_data_integrity(data: pd.DataFrame) -> dict[str, Any]:
        """
        Validate data integrity and return summary statistics.

        Args:
            data: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        if data.empty:
            return {"valid": False, "message": "DataFrame is empty"}

        validation: dict[str, Any] = {
            "valid": True,
            "total_rows": len(data),
            "date_range": {
                "start": data.index.min().isoformat() if len(data) > 0 else None,
                "end": data.index.max().isoformat() if len(data) > 0 else None,
            },
            "missing_values": {},
            "data_types": {},
            "issues": [],
        }

        # Check data types
        for col in ["open", "high", "low", "close", "volume"]:
            if col in data.columns:
                validation["data_types"][col] = str(data[col].dtype)
                missing_count = data[col].isna().sum()
                validation["missing_values"][col] = missing_count

                if missing_count > 0:
                    validation["issues"].append(f"Column {col} has {missing_count} missing values")

        # Check OHLC relationships
        if all(col in data.columns for col in ["open", "high", "low", "close"]):
            invalid_high = (data["high"] < data[["open", "close"]].max(axis=1)).sum()
            invalid_low = (data["low"] > data[["open", "close"]].min(axis=1)).sum()

            if invalid_high > 0:
                validation["issues"].append(f"Found {invalid_high} invalid high prices")
            if invalid_low > 0:
                validation["issues"].append(f"Found {invalid_low} invalid low prices")

        # Check for duplicates
        duplicates = data.index.duplicated().sum()
        if duplicates > 0:
            validation["issues"].append(f"Found {duplicates} duplicate timestamps")

        # Check for negative values
        for col in ["open", "high", "low", "close"]:
            if col in data.columns:
                negative_count = (data[col] < 0).sum()
                if negative_count > 0:
                    validation["issues"].append(
                        f"Column {col} has {negative_count} negative values"
                    )

        if validation["issues"]:
            validation["valid"] = False

        return validation
