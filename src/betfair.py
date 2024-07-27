import requests
import pandas as pd
import logging

class Betfair:
    def __init__(self, api_key, auth_code):
        self.api_key = api_key
        self.auth_code = auth_code
        self.base_url = "https://api.betfair.com/exchange/account/json-rpc/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'X-Application': self.api_key,
            'X-Authentication': self.auth_code,
            'Content-Type': 'application/json'
        })

    def check_connection(self):
        response = self.session.post(
            self.base_url,
            json={"jsonrpc": "2.0", "method": "AccountAPING/v1.0.getAccountFunds", "params": {}, "id": 1}
        )
        if response.status_code != 200 or 'error' in response.json():
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception("Failed to connect to Betfair. Please check your API key and authentication code.")

    def account_balance(self):
        response = self.session.post(
            self.base_url,
            json={"jsonrpc": "2.0", "method": "AccountAPING/v1.0.getAccountFunds", "params": {}, "id": 1}
        )
        result = response.json().get('result', {})
        return result.get('availableToBetBalance', 0)  

    def list_event_types(self):
        endpoint = "https://api.betfair.com/exchange/betting/rest/v1.0/"
        header = {
            'X-Application': self.api_key,
            'X-Authentication': self.auth_code,
            'Content-Type': 'application/json'
        }
        json_req = '{"filter": {}}'
        url = endpoint + "listEventTypes/"
        response = self.session.post(url, data=json_req, headers=header)
        
        if response.status_code == 200:
            json_data = response.json()
            data = [{'id': event['eventType']['id'], 'name': event['eventType']['name']} for event in json_data]
            df = pd.DataFrame(data)
            return df
        else:
            logging.error(f"Failed to retrieve data. Status code: {response.status_code}")
            return pd.DataFrame()

    def list_market_horse(self, start_time, end_time):
        api_url = 'https://api.betfair.com/betting/json-rpc/v1'
        headers = {
            'X-Application': self.api_key,
            'X-Authentication': self.auth_code,
            'Content-Type': 'application/json'
        }
        payload = {
            "jsonrpc": "2.0",
            "method": "SportsAPING/v1.0/listMarketCatalogue",
            "params": {
                "filter": {
                    "eventTypeIds": ["7"],
                    "marketCountries": ["GB"], 
                    "marketTypeCodes": ["WIN"], 
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

        response = self.session.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            if 'result' in response_data:
                market_data = response_data['result']
                df = pd.json_normalize(market_data)
                if 'runners' in df.columns:
                    df_exploded = df.explode('runners')
                    df_normalized = pd.json_normalize(df_exploded['runners'])
                    result_df = pd.concat([df_exploded.drop(columns='runners').reset_index(drop=True), df_normalized.reset_index(drop=True)], axis=1)
                    result_df.to_csv('test1.csv', index=False)
                    return result_df
                else:
                    logging.warning("No 'runners' column found in the DataFrame.")
                    return None
            else:
                logging.error("No 'result' key found in the response JSON.")
                return None
        else:
            logging.error(f"Request failed with status code: {response.status_code}")
            logging.error(response.text)
            return None

    def get_market_price_data(self, market_id):
        api_url = 'https://api.betfair.com/betting/json-rpc/v1'
        headers = {
            'X-Application': self.api_key,
            'X-Authentication': self.auth_code,
            'Content-Type': 'application/json'
        }
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

        response = self.session.post(api_url, json=price_payload, headers=headers)
        if response.status_code == 200:
            price_data = response.json().get('result')
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
                            "size": first_entry.get('size')
                        })
                return extracted_data
            else:
                logging.warning(f"No price data available for market {market_id}")
                return None
        else:
            logging.error(f"Failed to fetch price data for market {market_id}")
            return None

    def join_market_and_price(self, start_time, end_time):
        market_data = self.list_market_horse(start_time, end_time)
        if market_data is not None and not market_data.empty:
            unique_market_ids = market_data['marketId'].unique().tolist()
           
