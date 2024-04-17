from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

class DataCleaning:
    @staticmethod
    def replace_nan(df, column_names):
        """
        Replace Nan values with 0 for specified columns in a df

        Parameters:
        df (pd.DataFrame): input df
        column_names (list): list of column names to replace NaN with 0

        Returns:
        pandas.DataFrame: DataFrame with NaN values replaced with 0

        Example Usage:
        > cleaned_df = DataCleaning.replace_nan(df, ['A', 'B'])
        """

        df_replaced = df.copy()
        df_replaced[column_names] = df_replaced[column_names].fillna(0)
        return df_replaced
    
    @staticmethod
    def split_data(df, date_col='Race Time', course_col = 'Course', test_size = 0.2):
        """
        Split a dataframe whilst ensuring no leakage between races

        Parameters:
        df (pd.DataFrame): input df
        date_col (string): column name
        course_col (string): column name
        test_size (float): proportion to be used for the test df

        Returns:
        pandas.Dataframe: training df
        pandas.DataFrame: test df
        """
        grouped = df.groupby([date_col, course_col])
        train_indices, test_indices = [], []

        for _, group in grouped:
            train_idx, test_idx = train_test_split(group.index, test_size=test_size, shuffle=False)
            train_indices.extend(train_idx)
            test_indices.extend(test_idx)

        train_data = df.loc[train_indices]
        test_data = df.loc[test_indices]

        return train_data, test_data

    @staticmethod
    def normalize_columns(df, column_names):
        """
        Normalize specified columns in a df using MinMaxScaler.
        
        Parameters:
        df (pd.DataFrame): input df
        column_names (list): list of column names to normalize

        Returns:
        pandas.DataFrame: DataFrame with specified columns normalized

        Example Usage:
        > normalized_df = DataCleaning.normalize_columns(df, ['A', 'B'])
        """
        
        scaler = MinMaxScaler()
        df_normalized = df.copy()
        df_normalized[column_names] = scaler.fit_transform(df[column_names])
        return df_normalized
    
    @staticmethod
    def standardize_columns(df, column_names):
        """
        Standardize specified columns in a df using StandardScaler

        Parameters:
        df (pd.DataFrame): input df
        column_names (list): list of column names to standardize

        Returns:
        pandas.DataFrame: DataFrame with specified columns standardized

        Example Usage:
        > standardized_df = DataCleaning.standardized_columns(df, ['A', 'B'])
        """

        scaler = StandardScaler()
        df_standardized = df.copy()
        df_standardized[column_names] = scaler.fit_transform(df[column_names])
        return df_standardized
