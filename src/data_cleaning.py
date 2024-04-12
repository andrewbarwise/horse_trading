from sklearn.preprocessing import MinMaxScaler, StandardScaler

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
