import betfairlightweight
import pandas as pd
import logging

class Betfair:
    def __init__(self, username, password, app_key, interactive_login=True):
        self.username = username
        self.password = password
        self.app_key = app_key
        self.client = betfairlightweight.APIClient(username, password, app_key=app_key)

        if interactive_login:
            self.client.login_interactive()  # Use interactive login if no certificates are set up

    def check_connection(self):
        try:
            # Since interactive login is used during initialization, no need to call login() again
            if not self.client.session_token:
                raise Exception("Failed to obtain session token. Please check your credentials and app key.")
        except Exception as e:
            raise Exception(f"Error during Betfair connection: {str(e)}")

    def account_balance(self):
        try:
            account_funds = self.client.get_account_funds()
            return account_funds.available_to_bet_balance
        except Exception as e:
            logging.error(f'Failed to retrieve account balance: {e}')
            return 0

    def list_market_horse(self, start_time, end_time):
        try:
            market_filter = betfairlightweight.filters.market_filter(
                event_type_ids=['7'],
                market_countries=['GB'],
                market_type_codes=['WIN'],
                market_start_time={'from': start_time, 'to': end_time}
            )

            market_catalogues = self.client.betting.list_market_catalogue(
                filter=market_filter,
                market_projection=[
                    'MARKET_START_TIME',
                    'RUNNER_METADATA',
                    'RUNNER_DESCRIPTION',
                    'EVENT_TYPE',
                    'EVENT',
                    'COMPETITION'
                ],
                max_results=200
            )

            data = []
            for market in market_catalogues:
                for runner in market.runners:
                    data.append({
                        'marketId': market.market_id,
                        'marketName': market.market_name,
                        'event': market.event.name,
                        'runnerid': runner.selection_id,
                        'runnerName': runner.runner_name,
                        'marketStartTime': market.market_start_time
                    })

            df = pd.DataFrame(data)
            df.to_csv('test1.csv', index=False)

        except Exception as e:
            logging.error(f'Failed to list market: {e}')
            return pd.DataFrame()

    def get_market_price_data(self, market_id):
        try:
            price_data = self.client.betting.list_market_book(
                market_ids=[market_id],
                price_projection=betfairlightweight.filters.price_projection(price_data=['EX_BEST_OFFERS'])
            )
            if price_data:
                market_book = price_data[0]
                extracted_data = []

                for runner in market_book.runners:
                    first_back_offer = runner.ex.available_to_back[0] if runner.ex.available_to_back else {'price': None, 'size': None}
                    first_lay_offer = runner.ex.available_to_lay[0] if runner.ex.available_to_lay else {'price': None, 'size': None}

                    extracted_data.append({
                        'marketId': market_id,
                        'selectionId': runner.selection_id,
                        'backPrice': first_back_offer['price'],
                        'backSize': first_back_offer['size'],
                        'layPrice': first_lay_offer['price'],
                        'laySize': first_lay_offer['size']
                    })
                return extracted_data
            else:
                logging.warning(f'No price data available for market {market_id}')
                return None
        except Exception as e:
            logging.error(f'Failed to get market price data: {e}')
            return None

    def join_market_and_price(self, start_time, end_time):
        market_data = self.list_market_horse(start_time, end_time)

        if market_data is not None and not market_data.empty:
            unique_market_ids = market_data['marketId'].unique().tolist()

            all_price_data = []
            for market_id in unique_market_ids:
                price_data = self.get_market_price_data(market_id)

                if price_data:
                    all_price_data.extend(price_data)

            if all_price_data:
                price_df = pd.DataFrame(all_price_data)
                combined_df = pd.merge(market_data, price_df, on='marketId')
                return combined_df
        else:
            logging.warning('No market data available.')
            return None
