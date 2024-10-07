from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split

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
    def split_data(df, date_col='Race Time', course_col='Course', test_size=0.2):
        """
        Split a dataframe whilst ensuring no leakage between races.

        Parameters:
        df (pd.DataFrame): input dataframe
        date_col (str): column name for the date of the race
        course_col (str): column name for the course
        test_size (float): proportion to be used for the test dataframe

        Returns:
        tuple: training dataframe, test dataframe

        Example Usage:
        train_data, test_data = split_data(df=df)
        """
        # Create a unique identifier for each race
        df['race_id'] = df[date_col].astype(str) + '_' + df[course_col].astype(str)
        
        # Get unique races
        unique_races = df['race_id'].unique()
        
        # Split the races into train and test sets
        train_races, test_races = train_test_split(unique_races, test_size=test_size, shuffle=True, random_state=42)
        
        # Split the dataframe based on the race ids
        train_data = df[df['race_id'].isin(train_races)]
        test_data = df[df['race_id'].isin(test_races)]
        
        # Drop the temporary 'race_id' column
        train_data = train_data.drop(columns=['race_id'])
        test_data = test_data.drop(columns=['race_id'])
        
        return train_data, test_data

    # Example usage
    # Assuming `df` is your dataframe
    # train_data, test_data = split_data(df=df)

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
