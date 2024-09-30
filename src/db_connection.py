import mysql.connector
import os
import pandas as pd

class DatabaseConnector:
    def __init__(self, database_name, password):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        #self.password = os.getenv('DB_PASSWORD')
        self.password = password
        self.database = database_name
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print('Connected to the database')
        except Exception as e:
            print(f'Error connecting to the database: {str(e)}')

    def disconnect(self):
        try:
            if self.connection.is_connected():
                self.connection.close()
                print('Disconnected from the database')
        except Exception as e:
            print(f'Error disconnectiong from the database: {str(e)}')


    def execute_query(self, query, data=None):
        if self.connection is None or not self.connection.is_connected():
            print('Database connection is not established')
            return None

        try:
            cursor = self.connection.cursor()
            if data:
                cursor.execute(query, data)  # Execute the query with data parameters
            else:
                cursor.execute(query)  # Execute the query without data parameters
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f'Error executing the query: {str(e)}')

    def fetch_data(self, query, data = None):
        if self.connection is None or not self.connection.is_connected():
            print('Database connection is not established')

        try: 
            cursor = self.connection.cursor(dictionary=True) # use dictionary cursor
            if data:
                cursor.execute(query, data) # execute the query with data parameters

            else:
                cursor.execute(query) # execute the query without data parameters
            result = cursor.fetchall() # fetch all rows as a dictionary
            cursor.close()

            # convert the list of dictionaries to a Pandas df.
            if result:
                df = pd.DataFrame(result)
                return df
            
            else: return None

        except Exception as e:
            print(f"Error fetching data from the database: {str(e)}")
            return None
        
    def save_data_frame(self, df, table_name, if_exists='replace', dtype_map=None, cursor=None):
        if self.connection is None or not self.connection.is_connected():
            print('Database connection is not established')
            return

        try:
            # Convert data types if a mapping is provided
            if dtype_map:
                df = df.astype(dtype_map)

            # Use the to_sql method to save the DataFrame to the database table
            df.to_sql(name=table_name, con=self.connection, if_exists=if_exists, index=False, dtype=dtype_map)

            print(f'DataFrame successfully saved to table {table_name}')

        except Exception as e:
            print(f'Error saving DataFrame to table {table_name}: {e}')
