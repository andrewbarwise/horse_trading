import os
import requests
import json
import pandas as pd
import betfairlightweight
from betfairlightweight import filters
from datetime import datetime, timedelta
import time

class MorningPrice:
    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
    
    def markets(self, start_time, end_time, trading):
        # Define filter for horse racing markets
        market_filter = betfairlightweight.filters.market_filter(
            event_type_ids=['7'],
            market_countries=['GB'],
            market_type_codes=['WIN'], 
            market_start_time={'from': start_time.isoformat(),
                            'to' : end_time.isoformat()}
        )

        # Request market catalogue for all horse races on the date
        results = trading.betting.list_market_catalogue(
            filter=market_filter,
            market_projection=["RUNNER_DESCRIPTION", 
                    "RUNNER_METADATA", 
                    "COMPETITION", 
                    "EVENT", 
                    "EVENT_TYPE", 
                    "MARKET_DESCRIPTION", 
                    "MARKET_START_TIME",],  # Include runner metadata
            max_results=1000  # Adjust based on expected number of races
        )

        return results
    
    def market_runner(self, results):
        # Initialize an empty list to store market and runner details
        data = []

        # Iterate over each market in the market catalogue
        for market in results:
            market_id = market.market_id
            market_name = market.market_name
            market_start_time = market.market_start_time
            market_type = market.description.market_type

            # Extract the location/venue of the race
            event = market.event
            race_location = event.venue if event else "Unknown Location"
            
            # Iterate over each runner in the market
            for runner in market.runners:
                runner_id = runner.selection_id
                runner_name = runner.runner_name
                
                # Append a dictionary with all relevant data to the list
                data.append({
                    'market_id': market_id,
                    'market_start_time': market_start_time,
                    'venue': race_location,
                    'market_type': market_type,
                    'selection_id': runner_id,
                    'horse_name': runner_name,
                })

        # Convert the list of dictionaries to a pandas DataFrame
        df1 = pd.DataFrame(data)
        
        return df1
    
    def market_id_list(self, df1):
        market_id_list = df1['market_id'].drop_duplicates().to_list()

        return market_id_list
    
    def market_books(self, market_id_list, trading):
        # Define a delay between requests
        delay = 0.05  # Delay in seconds

        # Loop through market IDs and fetch data with a delay
        market_books = []
        for market_id in market_id_list:
            market_book = trading.betting.list_market_book(
                market_ids=[market_id],
                price_projection=betfairlightweight.filters.price_projection(
                    price_data=betfairlightweight.filters.price_data(ex_all_offers=True)
                ),
            )
            market_books.append(market_book)
            
            # Sleep to avoid overloading the API
            time.sleep(delay)

        return market_books
    
    def morning_price(self, market_books1):
        data = []

        # Iterate over each list of MarketBook objects
        for book_list in market_books1:
            # Iterate over each MarketBook object in the current list
            for market_book in book_list:
                market_id = market_book.market_id
                status = market_book.status
                total_matched = market_book.total_matched

                # Iterate over each runner in the market
                for runner in market_book.runners:
                    runner_id = runner.selection_id
                    runner_status = runner.status
                    last_price_traded = runner.last_price_traded
                    runner_total_matched = runner.total_matched
                    
                    # Append a dictionary with all relevant data to the list
                    data.append({
                        'market_id': market_id,
                        'status': status,
                        'total_matched': total_matched,
                        'selection_id': runner_id,
                        'status': runner_status,
                        'morning_price': last_price_traded,
                    })



        # Convert the list of dictionaries into a DataFrame
        df2 = pd.DataFrame(data)

        df2 = df2[['market_id', 'selection_id', 'status', 'morning_price', 'total_matched']]
        return df2
    
    def join(self, df1, df2):

        df3 = df1.merge(df2, on = ['market_id', 'selection_id'], how = 'left')

        df3['market_id'] = df3['market_id'].astype(str)


        current_date = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{current_date}_data.csv"

        df3.to_csv('../data/daily/' + file_name, index=False)

        return df3