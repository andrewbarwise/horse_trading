import requests
import pandas as pd
import logging
import streamlit_pages as st
import streamlit as st

class Betfair:
    def __init__(self, key, code):
        self.betfair_api_key = key
        self.betfair_auth_code = code

    def check_connection(self):
        
        api_url = 'https://api.betfair.com/exchange/betting/rest/v1.0/'

        header = {
            'X-Application': self.betfair_api_key,
            'X-Authentication': self.betfair_auth_code,
            'content-type': 'application/json',
        }

        # Construct a simple JSON request (you can adjust this based on your needs)
        json_req = '{"filter": {}}'

        # Make a sample request to check the connection
        url = api_url + 'listEventTypes/'
        response = requests.post(url, data=json_req, headers=header)

        # Check the status code of the response
        if response.status_code == 200:
            st.success("Connection to Betfair successful!")
        else:
            st.error(f"Connection failed with status code: {response.status_code}")
            st.text(response.text)  # Display the error message if any

    
    def list_event_types(self):
        endpoint = "https://api.betfair.com/exchange/betting/rest/v1.0/"
        header = {
            'X-Application': self.betfair_api_key,
            'X-Authentication': self.betfair_auth_code,
            'content-type': 'application/json'
        }
        json_req = '{"filter": {}}'
        url = endpoint + "listEventTypes/"
        response = requests.post(url, data=json_req, headers=header)
        
        # Check if the API call was successful
        if response.status_code == 200:
            # Extract 'id' and 'name' from 'eventType' for each entry in the JSON response
            json_data = response.json()
            data = [{'id': event['eventType']['id'], 'name': event['eventType']['name']} for event in json_data]
            
            # Create a DataFrame
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return pd.DataFrame()  # Return an empty DataFrame on failure
        
    def account_balance(self):
        account_balance_url = 'https://api.betfair.com/exchange/account/json-rpc/v1'

        headers = {
            'X-Application': self.betfair_api_key,
            'X-Authentication': self.betfair_auth_code,
            'Content-Type': 'application/json',
        }

        payload = {
            "jsonrpc": "2.0",
            "method": "AccountAPING/v1.0/getAccountFunds",
            "params": {},
            "id": 1
        }

        try:
            response = requests.post(account_balance_url, json=payload, headers=headers)

            if response.status_code == 200:
                balance = response.json()['result']['availableToBetBalance']
                return balance
            else:
                logging.error(f"Failed to retrieve account balance. Status code: {response.status_code}")
                return None  # Return None to indicate failure

        except requests.RequestException as e:
            logging.exception(f"Request Exception occurred: {e}")
            return None  # Return None to indicate exception/error
        
    def list_market_horse(self, start_time, end_time):
        api_url = 'https://api.betfair.com/betting/json-rpc/v1'  # Adjust the API endpoint as needed

        # Construct the request headers with authentication
        headers = {
            'X-Application': self.betfair_api_key,
            'X-Authentication': self.betfair_auth_code,
            'Content-Type': 'application/json',
        }

        # Construct the JSON payload
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketCatalogue",
            "params": {
                "filter": {
                    "eventTypeIds": ["7"],
                    "marketTypeCodes": ["WIN"],  # can add "PLACE";  ["WIN", "PLACE"]
                    "marketStartTime": {
                        "from": start_time,
                        "to": end_time
                    }
                },
                "maxResults": "200",
                "marketProjection": [
                    "MARKET_START_TIME",
                    "RUNNER_METADATA",
                    "RUNNER_DESCRIPTION",
                    "EVENT_TYPE",
                    "EVENT",
                    "COMPETITION"
                ]
            },
            "id": 1
        }

        # Send the API request
        response = requests.post(api_url, json=payload, headers=headers)

        # Parse JSON response and create a DataFrame
        if response.status_code == 200:
            response_data = response.json()
            
            if 'result' in response_data:
                market_data = response_data['result']
                
                # Convert JSON to DataFrame
                df = pd.json_normalize(market_data)

                # Explode 'runners' column
                if 'runners' in df.columns:
                    df_exploded = df.explode('runners')
                    df_normalized = pd.json_normalize(df_exploded['runners'])
                    
                    # Merge DataFrames on index
                    result_df = pd.concat([df_exploded.drop(columns='runners').reset_index(drop=True), df_normalized.reset_index(drop=True)], axis=1)
                    
                    # Save DataFrame to CSV (Optional)
                    result_df.to_csv('test1.csv', index=False)  # Saving the DataFrame to test1.csv

                    return result_df
                else:
                    print("No 'runners' column found in the DataFrame.")
                    return None
            else:
                print("No 'result' key found in the response JSON.")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)  # Display the error message if any
            return None
        
    def get_market_price_data(self, market_id):
        api_url = 'https://api.betfair.com/betting/json-rpc/v1'  # Adjust the API endpoint as needed

        # Construct the request headers with authentication
        headers = {
            'X-Application': self.betfair_api_key,
            'X-Authentication': self.betfair_auth_code,
            'Content-Type': 'application/json',
        }

        # Construct the request payload for price data
        price_payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketBook",
            "params": {
                "marketIds": [market_id],
                "priceProjection": {
                    "priceData": ["EX_BEST_OFFERS"]
                }
            },
            "id": 1
        }

        # Send the API request for price data
        response = requests.post(api_url, json=price_payload, headers=headers)

        if response.status_code == 200:
            price_data = response.json().get('result')

            # Process the price data and extract the first "available to back" data for each runner
            if price_data:
                extracted_data = []
                for runner in price_data[0].get('runners', []):
                    ex_data = runner.get('ex', {})
                    available_to_back = ex_data.get('availableToBack', [])
                    if available_to_back:
                        first_entry = available_to_back[0]
                        extracted_data.append({
                            "marketId": market_id,
                            "selectionId": runner.get('selectionId'),
                            "price": first_entry.get('price'),
                            "size": first_entry.get('size'),
                            # Add more fields as needed
                        })

                return extracted_data
            else:
                print(f"No price data available for market {market_id}")
                return None
        else:
            print(f"Failed to fetch price data for market {market_id}")
            return None